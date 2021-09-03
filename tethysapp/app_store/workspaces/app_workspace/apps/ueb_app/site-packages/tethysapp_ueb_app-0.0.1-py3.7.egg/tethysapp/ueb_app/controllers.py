from oauthlib.oauth2 import TokenExpiredError

from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from tethys_sdk.gizmos import TextInput, SelectInput,DatePicker, GoogleMapView

from hs_restclient import HydroShare, HydroShareAuthOAuth2, HydroShareNotAuthorized, HydroShareNotFound


from .epsg_list import EPSG_List
from .model_run_utils import *
from .model_input_utils import *
from .user_settings import *

from tethys_sdk.permissions import login_required


# home page views
@login_required()
def home(request):
    """
    Controller for the app home page.
    """
    res_id = request.GET.get('res_id', None)
    context = {'res_id': res_id}

    return render(request, 'ueb_app/home.html', context)


# model input views and ajax submit
@login_required()
def model_input(request):
    res_id = request.GET.get('res_id', None)

    # bounding box
    north_lat = TextInput(display_text='North Latitude',
                          name='north_lat',
                          attributes={'required': True}
                          )

    south_lat = TextInput(display_text='South Latitude',
                          name='south_lat',
                          attributes={'required': True}
                          )

    west_lon = TextInput(display_text='West Longitude',
                         name='west_lon',
                         attributes={'required': True}
                          )

    east_lon = TextInput(display_text='East Longitude',
                         name='east_lon',
                         attributes={'required': True}
                         )

    # outlet point
    outlet_x = TextInput(display_text='Point Longitude',
                       name='outlet_x',
                       # attributes={'required': False}
                       )

    outlet_y = TextInput(display_text='Point Latitude',
                       name='outlet_y',
                       # attributes={'required': False}
                       )

    # stream threshold
    stream_threshold = TextInput(
                       # display_text='Stream Threshold',
                       name='stream_threshold',
                       initial='1000',
                       attributes={'size': '40',}
                       )


    # epsg code
    epsg_code = SelectInput(display_text='',
                            name='epsg_code',
                            multiple=False,
                            options=EPSG_List,
                            initial=['5072 : NAD83(NSRS2007) / Conus Albers'],
                            attributes={'style': 'width:200px', 'required': True}
                            )

    # time period
    start_time = DatePicker(name='start_time',
                         display_text='Start Date',
                         autoclose=True,
                         format='yyyy/mm/dd',
                         start_date='2009/01/01',
                         end_date='2015/12/31',
                         initial='2010/10/01',
                         today_button=True,
                         multidate='1',
                         attributes={'required': True}
                        )

    end_time = DatePicker(name='end_time',
                            display_text='End Date',
                            autoclose=True,
                            format='yyyy/mm/dd',
                            start_date='2009/01/01',
                            end_date='2015/12/31',
                            initial='2011/09/30',
                            today_button=True,
                            multidate='1',
                            attributes={'required': True}
                            )

    # model resolution
    x_size = TextInput(display_text='X size(m)',
                       name='x_size',
                       initial='30',
                       # attributes={'required': True},
                       placeholder='integer value',
                       )

    y_size = TextInput(display_text='Y size(m)',
                       name='y_size',
                       initial='30',
                       # attributes={'required': True},
                       placeholder='integer value',
                       )

    dx_size = TextInput(display_text='dX size(m)',
                       name='dx_size',
                       initial='100',
                       attributes={'required': True},
                       placeholder='integer value',
                       )

    dy_size = TextInput(display_text='dY size(m)',
                        name='dy_size',
                        initial='100',
                        attributes={'required': True},
                        placeholder='integer value',
                        )

    # site initial parameters
    usic = TextInput(
        display_text='Energy content initial condition (kg m-3)',
        name='usic',
        placeholder='e.g. 0 (for no snow season)',
        # initial='0',
        attributes={'size': '40', 'required': True}
    )

    wsic = TextInput(
        display_text='Snow water equivalent initial condition (m)',
        name='wsic',
        placeholder='e.g. 0 (for no snow season)',
        # initial='0',
        attributes={'size': '40', 'required': True}
    )

    tic = TextInput(
        display_text='Snow surface dimensionless age initial condition',
        name='tic',
        placeholder='e.g. 0 (for no snow season)',
        # initial='0',
        attributes={'size': '40', 'required': True}
    )

    wcic = TextInput(
        display_text='Snow water equivalent of canopy condition(m)',
        name='wcic',
        placeholder='e.g. 0 (for no snow season)',
        # initial='0',
        attributes={'size': '40', 'required': True}
    )

    ts_last = TextInput(
        display_text=' Snow surface temperature one day prior to the model starting time (degree celsius)',
        name='ts_last',
        placeholder='e.g. 0 (for no snow season)',
        # initial='0',
        attributes={'size': '40', 'required': True}
    )

    # resource info
    res_title = TextInput(display_text='HydroShare resource title',
                       name='res_title',
                       placeholder='UEB model package',
                       attributes={'size': '40',
                                   # 'required': True
                                   }
                       )
    res_keywords = TextInput(display_text='HydroShare resource keywords',
                       name='res_keywords',
                       placeholder='Utah Energy Balance Model, Snowmelt',
                       attributes={'size': '40',
                                   # 'required': True
                                   }
                       )
    # context
    context = {'north_lat': north_lat,
               'south_lat': south_lat,
               'west_lon': west_lon,
               'east_lon': east_lon,
               'outlet_x': outlet_x,
               'outlet_y': outlet_y,
               'stream_threshold': stream_threshold,
               'epsg_code': epsg_code,
               'start_time': start_time,
               'end_time': end_time,
               'x_size': x_size,
               'y_size': y_size,
               'dx_size': dx_size,
               'dy_size': dy_size,
               'usic': usic,
               'wsic': wsic,
               'tic': tic,
               'wcic': wcic,
               'ts_last': ts_last,
               'res_title': res_title,
               'res_keywords': res_keywords,
               'res_id': res_id
               }

    return render(request, 'ueb_app/model_input.html', context)


@login_required()
def model_input_submit(request):
    # TODO: pass the token, client id, client secret to HydroDS to create new resource in HydroShare
    ajax_response = {}

    if request.is_ajax and request.method == 'POST':

        validation = validate_model_input_form(request)

        if validation['is_valid']:
            model_input_job = submit_model_input_job(validation['result'])
            ajax_response = model_input_job
        else:
            ajax_response['status'] = 'Error'
            ajax_response['result'] = ' '.join(validation['result'].values())

    else:
        ajax_response['status'] = 'Error'
        ajax_response['result'] = 'Please verify that the request is ajax call with post method'

    return HttpResponse(json.dumps(ajax_response))


# model run views and ajax submit
@login_required()
def model_run(request):
    try:

        # authentication:
        OAuthHS = get_OAuthHS(request)

        # get user editable model instance resource list
        hs = OAuthHS['hs']
        hs_editable_res_name_list = []

        for resource in hs.getResourceList(owner=OAuthHS.get('user_name'), types=["ModelInstanceResource"]):
            hs_editable_res_name_list.append((resource['resource_title'], resource['resource_id']))

        # get the initial list item
        res_id = request.POST.get('resource_list', None) if request.POST.get('resource_list', None) else request.GET.get('res_id', None)

        if res_id:
            initial = [option[0] for option in hs_editable_res_name_list if option[1] == res_id]
        else:
            if hs_editable_res_name_list:  # when there is model instance resource
                initial = [hs_editable_res_name_list[0][0]]
                res_id = hs_editable_res_name_list[0][1]
            else:  # when there is no model instance resource
                initial = ['No model instance resource']

        options = hs_editable_res_name_list if hs_editable_res_name_list else [('No model instance resource', '')]

        # get the resource metadata
        if res_id:
            model_resource_metadata = get_model_resource_metadata(hs, res_id)
        else:
            model_resource_metadata = dict.fromkeys(
            ['north_lat', 'south_lat', 'east_lon', 'west_lon', 'start_time', 'end_time', 'outlet_x', 'outlet_y',
             'epsg_code', 'cell_x_size', 'cell_y_size'], None)

    except Exception as e:
        print(e)
        options = [('Failed to retrieve the model instance resources list', '')]
        initial = ['Failed to retrieve the model instance resources list']
        model_resource_metadata = dict.fromkeys(
            ['north_lat', 'south_lat', 'east_lon', 'west_lon', 'start_time', 'end_time', 'outlet_x', 'outlet_y',
             'epsg_code', 'cell_x_size', 'cell_y_size'], None)

    finally:
        # resource list
        resource_list = SelectInput(
                                name='resource_list',
                                multiple=False,
                                options=options,
                                attributes={'style': 'width:200px', 'required': True},
                                initial=initial,
                                )

        # context
        context = {'resource_list': resource_list,
                   'user_name': OAuthHS.get('user_name'),
                   'res_id': request.GET.get('res_id', None),
                   'res_metadata': model_resource_metadata,
                   'client_id':OAuthHS.get('client_id'),
                   'client_secret': OAuthHS.get('client_secret'),
                   'token': OAuthHS.get('token')
                   }

    return render(request, 'ueb_app/model_run.html', context)


@login_required()
def model_run_submit_execution(request):
    if request.is_ajax and request.method == 'POST':
        res_id = request.POST['resource_list']
        OAuthHS = get_OAuthHS(request)
        if 'error' in OAuthHS.keys():
            ajax_response = {
                'status': 'Error',
                'result': OAuthHS['error']
            }

        else:
            # ajax_response = submit_model_run_job(res_id, OAuthHS, hydrods_name, hydrods_password)
            ajax_response = submit_model_run_job_single_call(res_id, OAuthHS)

    else:
        ajax_response = {
            'status': 'Error',
            'result': 'Please verify that the request is ajax call with post method'
        }

    return HttpResponse(json.dumps(ajax_response))


# check status views and ajax submit
@login_required()
def check_status(request):
    # res_id
    res_id = request.GET.get('res_id', None)

    # job_id
    job_id = TextInput(display_text='',
                       name='job_id',
                       placeholder='Enter the Job ID Here',
                       attributes={'required': True, 'style': 'width:800px;height:41px'}
                       )
    OAuthHS = get_OAuthHS(request)
    job_list, job_check_status = get_job_status_list(hs_username=OAuthHS['user_name'])

    context = {
               'job_check_status': job_check_status,
               'job_id': job_id,
               'res_id': res_id,
               'job_list': job_list
               }

    return render(request, 'ueb_app/check_status.html', context)


def get_job_status_list(hs_username):
    try:
        url = 'http://129.123.41.218:20199/api/dataservice/job/check_job_status'
        auth = (hydrods_name, hydrods_password)
        payload = {
            'extra_data': 'HydroShare: ' + hs_username
        }

        response = requests.get(url, params=payload, auth=auth)

        if response.status_code == 200:
            result = json.loads(response.text)
            for job in result['data'][:]:
                start_time = datetime.strptime(job['start_time'][:10], '%Y-%m-%d')
                timedelta = datetime.now() - start_time
                if timedelta.days >= 30:
                   result['data'].remove(job)
            job_list = result['data']
            job_check_status = 'success'
        else:
            job_list = []
            job_check_status = 'error'

    except Exception as e:
        print(e)
        job_list = []
        job_check_status = 'error'

    return job_list, job_check_status


# help views
@login_required()
def help_page(request):
    # res_id
    res_id = request.GET.get('res_id', None)
    context = {'res_id': res_id}
    return render(request, 'ueb_app/help.html', context)


# get hs object through oauth
def get_OAuthHS(request):
    OAuthHS = {}

    try:
        hs_hostname = "www.hydroshare.org"

        client_id = getattr(settings, "SOCIAL_AUTH_HYDROSHARE_KEY", None)
        client_secret = getattr(settings, "SOCIAL_AUTH_HYDROSHARE_SECRET", None)

        # this line will throw out from django.core.exceptions.ObjectDoesNotExist if current user is not signed in via HydroShare OAuth
        token = request.user.social_auth.get(provider='hydroshare').extra_data['token_dict']
        user_name = request.user.social_auth.get(provider='hydroshare').uid

        auth = HydroShareAuthOAuth2(client_id, client_secret, token=token)
        hs = HydroShare(auth=auth, hostname=hs_hostname)

        OAuthHS['hs'] = hs
        OAuthHS['token'] = token
        OAuthHS['client_id'] = client_id
        OAuthHS['client_secret'] = client_secret
        OAuthHS['user_name'] = user_name

    except ObjectDoesNotExist as e:
        OAuthHS['error'] = 'ObjectDoesNotExist: ' + e.message
    except TokenExpiredError as e:
        OAuthHS['error'] = 'TokenExpiredError ' + e.message
    except HydroShareNotAuthorized as e:
        OAuthHS['error'] = 'HydroShareNotAuthorized' + e.message
    except HydroShareNotFound as e:
        OAuthHS['error'] = 'HydroShareNotFound' + e.message
    except Exception as e:
        OAuthHS['error'] = 'Authentication Failure:' + e.message

    return OAuthHS


# test part #
def test(request):
    """
    Controller for the app home page.
    """
    context = {}

    return render(request, 'ueb_app/test.html', context)


def test_submit(request):

    return HttpResponse(json.dumps({'name':'name'}))
