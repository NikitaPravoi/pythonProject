from django.shortcuts import render

def index(request):
    session = request.session

    demo_count = session.get('django_plotly_dash', {})

    ind_use = demo_count.get('ind_use', 0)
    ind_use += 1
    demo_count['ind_use'] = ind_use
    session['django_plotly_dash'] = demo_count

    # Use some of the information during template rendering
    context = {'ind_use': ind_use}

    return render(request, 'app1/index.html', context)