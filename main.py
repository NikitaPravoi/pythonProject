import plotly.graph_objects as go
import pandas as pd
from dash import Dash, dcc, html, Input, Output, ctx
from database import mydb
from datetime import datetime, timedelta

# Собираем данные
df = pd.read_excel("machinery.xlsx")
df['Подрядчик'] = df['Подрядчик'].str.strip()

df2 = pd.read_excel("rudnik.xlsx",
                    sheet_name='Мобилизация подрядчика ')

df3 = pd.DataFrame({'Персонал': ['ИТР', 'Механизатор', 'Рабочий', 'Вспомогательный рабочий', 'Итого; персонал'],
                    'Количество, факт': [88, 91, 459, 48, 686],
                    'Изменение за период': [-6, -1, 15, 14, 22],
                    'Обеспеченность (% от плана)': [84, 90, 42, 63, 70]})

df4 = pd.DataFrame({'Техника': ['Основная',  'Вспомогательная', 'Итого; техника'],
                    'Количество, факт': [25, 19, 44],
                    'Изменение за период': [3, 1, 4],
                    'Обеспеченность (% от плана)': [72, 62, 70]})

sql = "SELECT * FROM organizations"
sql_df = pd.read_sql(sql, con=mydb)

# Внешний стиль CSS
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

# Разметка приложения
app.layout = html.Div([
    # Графики с выборкой по техники и персонала по всем подрядчикам
    html.Div([html.Div([dcc.Graph(id='all-contractor-machinery', config={'displaylogo': False})], className='six columns'),
              html.Div([dcc.Graph(id='all-contractor-personnel', config={'displaylogo': False})], className='six columns')],
             className='row', style={
            'font-family': 'arial',
            'z-index': 0}),
    html.Br(),
    html.Div([
            # Селектор выбора подрядчика
            dcc.Dropdown(
                id="contractor-dropdown",
                searchable=True,
                placeholder='Выбор подрядчика...',
                options=[{'label': x, 'value': x} for x in sql_df['contractor'].unique()],
                value='',
                style={
                    'font-family': 'arial',
                    'border-style': 'solid',
                    'border-color': '#EB8B2D',
                    'border-width': '1px',
                    'border-radius': '4px',
                    'width': '240px',
                    'margin-right': '20px',
                }
            ),
            # Селектор выбора техники
            dcc.Dropdown(
                id="machinery-dropdown",
                searchable=True,
                placeholder='Выбор техники...',
                options=[],
                value='',
                style={
                    'font-family': 'arial',
                    'border-style': 'solid',
                    'border-color': '#EB8B2D',
                    'border-width': '1px',
                    'border-radius': '4px',
                    'width': '340px',
                    'margin-right': '20px',
                }
            ),
            # Селектор выборки дат, по умолчанию - от минимального доступного значения до максимального
            dcc.DatePickerRange(
                    id='date-picker-range',
                    min_date_allowed=min(df2['Месяц, Год']),
                    max_date_allowed=max(df2['Месяц, Год']),
                    start_date=min(df2['Месяц, Год']),
                    end_date=max(df2['Месяц, Год']),
                    style={
                        'font-family': 'arial',
                        'margin-right': '20px',
                        'color': '#EB8B2D',
                        'height': '30px',
                    }
                ),
            # Три кнопки для определения шага в календаре
            html.Button('Сутки', id='button-date-last-day', style={'margin-right': '20px', 'background-color': 'white',
                      'color': '#EB8B2D', 'border': '1px solid #EB8B2D'}),
            html.Button('Месяц', id='button-date-last-month', style={'margin-right': '20px', 'color': '#EB8B2D',
                                                                     'border': '1px solid #EB8B2D'}),
            html.Button('Год', id='button-date-last-year', style={'color': '#EB8B2D', 'border': '1px solid #EB8B2D'})
    ], className='twelve columns', style={'display': 'flex'}),
    html.Div([
        html.Div([
            # Два графика с гистограммой по персоналу в зависимости от выбранного подрядчика из contractor-dropdown
            dcc.Tabs([
                dcc.Tab(label='Персонал', children=[dcc.Graph(id='personnel-graph', style={'font-family': 'arial'},
                                                              config={'displaylogo': False})], selected_style={
                                                                                        'border-top': '2px solid #EB8B2D', 'fontWeight': 'bold'}),
                dcc.Tab(label='Весь персонал', children=[dcc.Graph(id='all-personnel-graph', config={'displaylogo': False})],
                        selected_style={
                            'border-top': '2px solid #EB8B2D', 'fontWeight': 'bold'})
            ], style={'margin-top': '20px'}),
            # Контейнер в который будет вставлена таблица с статистикой за отчетный период по персоналу
            html.Div(id='table-personnel', children=[], className='center'),
            # Контейнер в который будет вставлена таблица с статистикой за отчетный период по технике
            html.Div(id='table-machinery', children=[], style={
                  'marginLeft': 'auto', 'marginRight': 'auto',
                  'border-style': 'solid',
                  'border-color': '#EB8B2D',
                  'border-width': '2px',
                  'border-radius': '4px',
                  })
        ], className='six columns', style={'font-family': 'arial'}),
        html.Div([
            # Два графика с гистограммой по технике в зависимости от выбранного подрядчика из contractor-dropdown ...
            # и также конкретно выбранной техники из machinery-dropdown
            dcc.Tabs([
                dcc.Tab(label='Техника', children=[dcc.Graph(id="machine-graph", style={'font-family': 'arial'},
                                                             config={'displaylogo': False})],
                        selected_style={'border-top': '2px solid #EB8B2D', 'fontWeight': 'bold'}),
                dcc.Tab(label='Вся техника', children=[dcc.Graph(id='all-machinery-graph',
                                                                 config={'displaylogo': False})],
                        selected_style={'border-top': '2px solid #EB8B2D', 'fontWeight': 'bold'})

            ], style={'margin-top': '20px'}),
        ], className='six columns', style={"float": "right"})
    ], className='row'),
html.Div([
        html.Header([
            # Закрепленная шапка сайта
            html.H4(['Мобилизация подрядчиков'], style={'margin': '10px'})
        ])
    ], style={
            'font-family': 'arial',
            'border-style': 'none none solid none',
            'border-color': '#EB8B2D',
            'display': 'block',
            'position': 'fixed',
            'top': 0,
            'left': 0,
            'width': '100%',
            'z-index': 9999,
            'background-color': 'white'}),
], style={'padding-top': '60px'})

# Передача коллбэков из одного селектора в другой (список техники по подрядчику)
@app.callback(
    Output("machinery-dropdown", "disabled"),
    Output("machinery-dropdown", "options"),
    Input("contractor-dropdown", "value"))
def set_dropdown(prorab):
    # Сортировка значений переданных в селектор по выбранному подрядчику
    if prorab in ['ООО «СветоСтрой 93»', 'ООО «Орикадинамик»']:
        df_new = df[df['Подрядчик'] == prorab]
        return False, [{'label': x, 'value': x} for x in df_new['Техника наименование'].unique()]
    else:
        # Значений нет - селектор выключается и выбор в нем - будет недоступен
        df_new = df2[df2['Подрядчик'] == prorab]
        return True, []


# Составление графика по технике
@app.callback(
    Output("machine-graph", "figure"),
    Input("machinery-dropdown", "value"),
    Input("contractor-dropdown", "value"),
    Input("date-picker-range", "start_date"),
    Input("date-picker-range", "end_date"))
def make_machinery_graph(machine, prorab, start_date, end_date):
    if prorab in ['ООО «СветоСтрой 93»', 'ООО «Орикадинамик»']:
        # Сортировка датафрейма по выбранной технике
        df_graph = df[df['Техника наименование'] == machine]
        # Сортировка по выбранным датам
        if start_date and end_date:
            df_graph = df_graph[(df_graph['Дата'] >= start_date) & (df_graph['Дата'] <= end_date)]
        # График
        fig = go.Figure(data=[
            go.Bar(name='План', x=df_graph['Дата'], y=df_graph['Техника кол-во(ПЛАН)'], marker=dict(color='#5E5C5C'),
                   text=df_graph['Техника кол-во(ПЛАН)'], hovertext=df_graph['БВР/ГКР'], hoverinfo="text"),
            go.Bar(name='Факт', x=df_graph['Дата'], y=df_graph['Техника кол-во(ФАКТ)'], marker=dict(color='#EB8B2D'),
                   text=df_graph['Техника кол-во(ФАКТ)'], hovertext=df_graph['БВР/ГКР'], hoverinfo="text")
        ])
        fig.update_layout(title='Техника')
        fig.update_layout(barmode='group', modebar_remove=['zoom', 'pan', 'select', 'zoomIn', 'zoomOut', 'lasso'],
                          legend=dict(x=-0.2,
                                      y=1,
                                      traceorder="normal",
                                      font=dict(
                                          family="arial",
                                          size=12,
                                          color="black")))
        fig.update_xaxes(tickangle=-45, tickson='boundaries', tickvals=df_graph["Дата"])
        fig.update_traces(textfont_size=18, textangle=0, textposition="inside", cliponaxis=True, hovertemplate=f"")
        return fig
    else:
        # Сортировка датафрейма по выбранному подрядчику
        df_graph = df2[df2['Подрядчик'] == prorab]
        # Сортировка по выбранным датам
        if start_date and end_date:
            df_graph = df_graph[(df_graph['Месяц, Год'] >= start_date) & (df_graph['Месяц, Год'] <= end_date)]
        # График
        fig = go.Figure(data=[
            go.Bar(name='План', x=df_graph['Месяц, Год'], y=df_graph['Техника/План'], marker=dict(color='#5E5C5C'),
                   text=df_graph['Техника/План'], hovertext=df_graph['Объект WBS'], hoverinfo="text"),
            go.Bar(name='Факт', x=df_graph['Месяц, Год'], y=df_graph['Техника/Факт'], marker=dict(color='#EB8B2D'),
                   text=df_graph['Техника/Факт'], hovertext=df_graph['Объект WBS'], hoverinfo="text")
        ])
        fig.update_xaxes(tickangle=-45, tickson='boundaries', tickvals=df_graph["Месяц, Год"])
        fig.update_traces(textfont_size=18, textangle=0, textposition="inside", cliponaxis=True, hovertemplate=f"")
        fig.update_layout(title='Техника подрядчика')
        fig.update_layout(barmode='group', modebar_remove=['zoom', 'pan', 'select', 'zoomIn', 'zoomOut', 'lasso'],
                          # display_logo=False,
                          legend=dict(x=-0.2,
                                      y=1,
                                      traceorder="normal",
                                      font=dict(
                                          family="arial",
                                          size=12,
                                          color="black")))
        return fig


# Составление графика по персоналу
@app.callback(
    Output("personnel-graph", "figure"),
    Input("machinery-dropdown", "value"),
    Input("contractor-dropdown", "value"),
    Input("date-picker-range", "start_date"),
    Input("date-picker-range", "end_date"))
def make_personnel_graph(personnel, prorab, start_date, end_date):
    if prorab in ['ООО «СветоСтрой 93»', 'ООО «Орикадинамик»']:
        # Сортировка датафрейма по выбранному подрядчику
        df_graph = df[df['Техника наименование'] == personnel]
        # Сортировка по выбранным датам
        if start_date and end_date:
            df_graph = df_graph[(df_graph['Дата'] >= start_date) & (df_graph['Дата'] <= end_date)]
        # График
        fig = go.Figure(data=[
            go.Bar(name='План', x=df_graph['Дата'], y=df_graph['Людей кол-во(ПЛАН)'], marker=dict(color='#5E5C5C'),
                   text=df_graph['Людей кол-во(ПЛАН)'], hovertext=df_graph['БВР/ГКР'], hoverinfo="text"),
            go.Bar(name='Факт', x=df_graph['Дата'], y=df_graph['Людей кол-во(ФАКТ)'], marker=dict(color='#EB8B2D'),
                   text=df_graph['Людей кол-во(ФАКТ)'], hovertext=df_graph['БВР/ГКР'], hoverinfo="text")
        ])
        fig.update_layout(title='Персонал')
        fig.update_layout(barmode='group', modebar_remove=['zoom', 'pan', 'select', 'zoomIn', 'zoomOut', 'lasso'],
                          legend=dict(x=-0.2,
                                      y=1,
                                      traceorder="normal",
                                      font=dict(
                                          family="arial",
                                          size=12,
                                          color="black")))
        fig.update_xaxes(tickangle=-45, tickson='boundaries', tickvals=df_graph["Дата"])
        fig.update_traces(textfont_size=18, textangle=0, textposition="inside", cliponaxis=True, hovertemplate=f"")
        return fig
    else:
        # Сортировка датафрейма по выбранному подрядчику
        df_graph = df2[df2['Подрядчик'] == prorab]
        # Сортировка по выбранным датам
        if start_date and end_date:
            df_graph = df_graph[(df_graph['Месяц, Год'] >= start_date) & (df_graph['Месяц, Год'] <= end_date)]
        # График
        fig = go.Figure(data=[
            go.Bar(name='План', x=df_graph['Месяц, Год'], y=df_graph['Персонал/План'], marker=dict(color='#5E5C5C'),
                   text=df_graph['Персонал/План'], hovertext=df_graph['Объект WBS'], hoverinfo="text"),
            go.Bar(name='Факт', x=df_graph['Месяц, Год'], y=df_graph['Персонал/Факт'], marker=dict(color='#EB8B2D'),
                   text=df_graph['Персонал/Факт'], hovertext=df_graph['Объект WBS'], hoverinfo="text")
        ])
        fig.update_xaxes(tickangle=-45, tickson='boundaries', tickvals=df_graph["Месяц, Год"])
        fig.update_traces(textfont_size=18, textangle=0, textposition="inside", cliponaxis=True, hovertemplate=f"")
        fig.update_layout(title='Персонал подрядчика')
        fig.update_layout(barmode='group', modebar_remove=['zoom', 'pan', 'select', 'zoomIn', 'zoomOut', 'lasso'],
                          legend=dict(x=-0.2,
                                      y=1,
                                      traceorder="normal",
                                      font=dict(
                                          family="arial",
                                          size=12,
                                          color="black")))
        return fig


# Составление графика по всему персоналу по всем подрядчикам
@app.callback(
    Output("all-contractor-personnel", "figure"),
    Input("contractor-dropdown", "value"))
def make_personnel_values(smt):
    # Группирование данных по подрядчику и плану по персоналу и дальнейшая сортировка их по возрастанию
    max_personnel = sql_df.groupby('contractor')['personnel_plan'].max().sort_values(ascending=False)
    # График
    fig = go.Figure(data=[
        go.Bar(x=max_personnel.values, y=max_personnel.index, orientation='h', marker=dict(color='#EB8B2D'),
               text=max_personnel.values)
    ])
    fig.update_xaxes(tickangle=-45, tickson='boundaries', tickvals=sql_df['contractor'])
    fig.update_traces(textfont_size=18, textangle=0, textposition="inside", cliponaxis=True, hovertemplate=f"")
    fig.update_layout(title='Персонал по всем подрядчикам',
                      modebar_remove=['zoom', 'pan', 'select', 'zoomIn', 'zoomOut', 'lasso'],
                      xaxis=dict(showgrid=True),
                      yaxis=dict(showgrid=False, showline=True, linewidth=2, linecolor='black'))
    return fig


# Составление графика по всей техники по всем подрядчикам
@app.callback(
    Output("all-contractor-machinery", "figure"),
    Input("contractor-dropdown", "value"))
def make_machinery_values(smt):
    # Группирование данных по подрядчику и плану по технике и дальнейшая сортировка их по возрастанию
    max_machinery = df.groupby('Техника наименование')['Техника кол-во(ФАКТ)'].max().sort_values(ascending=False)
    # График
    fig = go.Figure(data=[
        go.Bar(x=max_machinery.values, y=max_machinery.index, orientation='h', marker=dict(color='#EB8B2D'),
               text=max_machinery.values)
    ])
    fig.update_xaxes(tickangle=-45, tickson='boundaries', tickvals=df['Подрядчик'])
    fig.update_traces(textfont_size=18, textangle=0, textposition="auto", cliponaxis=True, hovertemplate=f"")
    fig.update_layout(title='Техника по всем подрядчикам',
                      modebar_remove=['zoom', 'pan', 'select', 'zoomIn', 'zoomOut', 'lasso'],
                      xaxis=dict(showgrid=True),
                      yaxis=dict(showgrid=False, showline=True, linewidth=2, linecolor='black'))
    return fig


# Составление графика по всей техники подрядчика
@app.callback(
    Output("all-machinery-graph", "figure"),
    Input("contractor-dropdown", "value"),
    Input("date-picker-range", "start_date"),
    Input("date-picker-range", "end_date"))
def make_contractor_values(prorab, start_date, end_date):
    # Сортировка датафрейма по выбранному подрядчику
    df_graph = df[df['Подрядчик'] == prorab]
    # Сортировка по выбранным датам
    if start_date and end_date:
        df_graph = df_graph[(df_graph['Дата'] >= start_date) & (df_graph['Дата'] <= end_date)]
    # Группировка данных по дате и суммирование значений по конкретной дате
    max_machinery = df_graph.groupby('Дата')['Техника кол-во(ФАКТ)'].sum()
    max_machinery_plan = df_graph.groupby('Дата')['Техника кол-во(ПЛАН)'].sum()
    # График
    fig = go.Figure(data=[
        go.Bar(x=max_machinery_plan.index, y=max_machinery_plan.values, marker=dict(color='#5E5C5C'),
               text=max_machinery_plan.values, hovertext=prorab, hoverinfo="text", name='План'),
        go.Bar(x=max_machinery.index, y=max_machinery.values, marker=dict(color='#EB8B2D'),
               text=max_machinery.values, hovertext=prorab, hoverinfo="text", name='Факт')
    ])
    fig.update_xaxes(tickangle=-45, tickson='boundaries', tickvals=df_graph['Дата'])
    fig.update_traces(textfont_size=18, textangle=0, textposition="auto", cliponaxis=True, hovertemplate="")
    fig.update_layout(title=f'Вся техника по {prorab}',
                      modebar_remove=['zoom', 'pan', 'select', 'zoomIn', 'zoomOut', 'lasso'],
                      legend=dict(x=-0.2,
                                  y=1,
                                  traceorder="normal",
                                  font=dict(
                                      family="arial",
                                      size=12,
                                      color="black"))
                      )
    return fig


# Составление графика по всему персоналу подрядчика
@app.callback(
    Output("all-personnel-graph", "figure"),
    Input("contractor-dropdown", "value"),
    Input("date-picker-range", "start_date"),
    Input("date-picker-range", "end_date"))
def make_personnel_values(prorab, start_date, end_date):
    # Сортировка датафрейма по выбранному подрядчику
    df_graph = df[df['Подрядчик'] == prorab]
    # Сортировка по выбранным датам
    if start_date and end_date:
        df_graph = df_graph[(df_graph['Дата'] >= start_date) & (df_graph['Дата'] <= end_date)]
    # Группировка данных по дате и суммирование значений по конкретной дате
    max_personnel = df_graph.groupby('Дата')['Людей кол-во(ФАКТ)'].sum()
    max_personnel_plan = df_graph.groupby('Дата')['Людей кол-во(ПЛАН)'].sum()
    # График
    fig = go.Figure(data=[
        go.Bar(x=max_personnel_plan.index, y=max_personnel_plan.values, marker=dict(color='#5E5C5C'),
               text=max_personnel_plan.values, hovertext=prorab, hoverinfo="text", name='План'),
        go.Bar(x=max_personnel.index, y=max_personnel.values, marker=dict(color='#EB8B2D'),
               text=max_personnel.values, hovertext=prorab, hoverinfo="text", name='Факт')
    ])
    fig.update_xaxes(tickangle=-45, tickson='boundaries', tickvals=df_graph['Дата'])
    fig.update_traces(textfont_size=18, textangle=0, textposition="auto", cliponaxis=True, hovertemplate="")
    fig.update_layout(title=f'Весь персонал по {prorab}',
                      modebar_remove=['zoom', 'pan', 'select', 'zoomIn', 'zoomOut', 'lasso'],
                      legend=dict(x=-0.2,
                                  y=1,
                                  traceorder="normal",
                                  font=dict(
                                      family="arial",
                                      size=12,
                                      color="black"))
                      )
    return fig


# Отправка данный о таблице по персоналу
@app.callback(Output('table-personnel', 'children'),
              Input('contractor-dropdown', 'value'))
def make_personnel_table(smt):
    children = html.Table([
        html.Thead(
    html.Tr([html.Th([col], style={'textAlign': 'center'}) for col in df3.columns],
            style={"background-color": '#EB8B2D'}, className='header-row')
    ),
            html.Tbody([html.Tr([html.Td(df3.iloc[i][col], style={'textAlign': 'center'})
                                 if col != 'Обеспеченность (% от плана)'
                                 else html.Td(df3.iloc[i][col],
                                              style={'color': '#88192B', 'textAlign': 'center'} if df3.iloc[i][col] < 40 else
                                              {'color': '#CD441F', 'textAlign': 'center'} if df3.iloc[i][col] < 60 else
                                              {'color': '#FEDE5D', 'textAlign': 'center'} if df3.iloc[i][col] < 90 else
                                              {'color': '#B5DCA4', 'textAlign': 'center'} if df3.iloc[i][col] < 99 else
                                              {'color': '#4DA958', 'textAlign': 'center'})
                                 for col in df3.columns
                                 ]) for i in range(len(df3))
                        ])
        ], style={
                  'marginLeft': 'auto', 'marginRight': 'auto',
                  'border-style': 'solid',
                  'border-color': '#EB8B2D',
                  'border-width': '2px',
                  'border-radius': '4px',
                  })
    return children


# Отправка данных о таблице по технике
@app.callback(Output('table-machinery', 'children'),
              Input('contractor-dropdown', 'value'))
def make_personnel_table(smt):
    children = html.Table([
        html.Thead(html.Tr([
            html.Th([col], style={'textAlign': 'center'}) for col in df4.columns],
                           style={"background-color": '#EB8B2D'}, className='header-row')),
                html.Tbody([html.Tr([html.Td(df4.iloc[i][col], style={'textAlign': 'center'})
                                     if col != 'Обеспеченность (% от плана)'
                    else
                        html.Td(df4.iloc[i][col], style={'color': '#88192B', 'textAlign': 'center'}
                                                        if df4.iloc[i][col] < 40 else
                                                        {'color': '#CD441F', 'textAlign': 'center'}
                                                        if df4.iloc[i][col] < 60 else
                                                        {'color': '#FEDE5D', 'textAlign': 'center'}
                                                        if df4.iloc[i][col] < 90 else
                                                        {'color': '#B5DCA4', 'textAlign': 'center'}
                                                        if df4.iloc[i][col] < 99 else
                                                        {'color': '#4DA958', 'textAlign': 'center'})
                            for col in df4.columns
                        ]) for i in range(len(df4))
                    ])
                ])
    return children


# Обмен коллбэками между кнопками и dcc.DatePickerRange
@app.callback(
    [Output('date-picker-range', 'start_date'),
     Output('date-picker-range', 'end_date')],
    [Input('button-date-last-day', 'n_clicks'),
     Input('button-date-last-month', 'n_clicks'),
     Input('button-date-last-year', 'n_clicks')])
def set_date(start_clicks, month_clicks, year_clicks):
    changed_id = [p['prop_id'] for p in ctx.triggered][0]
    if 'button-date-last-day' in changed_id:
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    elif 'button-date-last-month' in changed_id:
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    elif 'button-date-last-year' in changed_id:
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    else:
        end_date = max(df2['Месяц, Год'])
        start_date = min(df2['Месяц, Год'])
    return start_date, end_date


if __name__ == '__main__':
    app.run_server(debug=True)
