from django.shortcuts import render
from tethys_sdk.permissions import login_required

@login_required()
def home(request):
    """
    Controller for the app home page.
    """

    context = {'modelID': request.GET.get('modelID', '')}

    return render(request, 'epanet_model_viewer/home.html', context)
