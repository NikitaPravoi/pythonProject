import mysql.connector
import pandas as pd

mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    passwd='12345678',
    database='testdb'
)
mycursor = mydb.cursor()

# sql = "RENAME TABLE organisations TO organizations"
#
# mycursor.execute(sql)
# mydb.commit()
# df = pd.read_excel("/Users/user/Downloads/Telegram Desktop/Реконструкция_таштагольского_рудника_13979.xlsx",
                    # sheet_name='Мобилизация подрядчика ')
# df.fillna(value='0', inplace=True)


# sql = '''INSERT INTO organisations (contractor, work_date, machinery_plan, machinery_fact, personnel_plan, personnel_fact, type_of_work) VALUES (%s, %s, %s, %s, %s, %s, %s)'''
# val = df[['Подрядчик', 'Месяц, Год', 'Техника/План', 'Техника/Факт', 'Персонал/План', 'Персонал/Факт', 'Объект WBS']].values.tolist()
#
# clean_val = []
# for row in val:
#     if pd.notnull(row[1]):
#         clean_row = (row[0].strip(), row[1].strftime('%Y-%m-%d'), row[2], row[3], row[4], row[5], row[6])
#         clean_val.append(clean_row)
#
# mycursor.executemany(sql, clean_val)

# mydb.commit()

