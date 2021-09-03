from django.http import JsonResponse
from django.contrib.auth.decorators import login_required


@login_required()
def get_customsettings(request):
    """
    sends the custom settings for the app
    """
    from .app import Malaria as App
    return JsonResponse({'threddsurl': App.get_custom_setting('threddsurl')})


@login_required()
def get_currentrisks(request):
    """
    sends the custom settings for the app
    """
    from .tools import definecurrentrisks
    return JsonResponse(definecurrentrisks())


@login_required()
def get_historicriskplot(request):
    """
    sends the historical risk plot for a district to be used by highcharts
    """
    from .tools import historicalriskplot
    import ast
    request = ast.literal_eval(request.body.decode('utf-8'))['ubigeo']
    return JsonResponse(historicalriskplot(request))
