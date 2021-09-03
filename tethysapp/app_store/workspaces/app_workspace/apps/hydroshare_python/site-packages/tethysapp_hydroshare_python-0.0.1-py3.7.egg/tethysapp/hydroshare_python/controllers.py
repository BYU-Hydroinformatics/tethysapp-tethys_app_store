from django.shortcuts import render
from tethys_sdk.permissions import login_required
from tethys_sdk.gizmos import Button
from tethys_sdk.gizmos import TextInput, DatePicker, SelectInput
from tethys_sdk.gizmos import DataTableView
from tethys_services.backends.hs_restclient_helper import get_oauth_hs
from django.shortcuts import redirect, reverse
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from hs_restclient import HydroShare, HydroShareAuthBasic
from django.utils.encoding import smart_str
from wsgiref.util import FileWrapper
import os
import tempfile
import zipfile
import json
from django.core import serializers




@login_required()
def home(request):
    """
    Controller for the app home page.
    """
    save_button = Button(
        display_text='',
        name='save-button',
        icon='glyphicon glyphicon-floppy-disk',
        style='success',
        attributes={
            'data-toggle':'tooltip',
            'data-placement':'top',
            'title':'Save'
        }
    )

    edit_button = Button(
        display_text='',
        name='edit-button',
        icon='glyphicon glyphicon-edit',
        style='warning',
        attributes={
            'data-toggle':'tooltip',
            'data-placement':'top',
            'title':'Edit'
        }
    )

    remove_button = Button(
        display_text='',
        name='remove-button',
        icon='glyphicon glyphicon-remove',
        style='danger',
        attributes={
            'data-toggle':'tooltip',
            'data-placement':'top',
            'title':'Remove'
        }
    )

    previous_button = Button(
        display_text='Previous',
        name='previous-button',
        attributes={
            'data-toggle':'tooltip',
            'data-placement':'top',
            'title':'Previous'
        }
    )

    next_button = Button(
        display_text='Next',
        name='next-button',
        attributes={
            'data-toggle':'tooltip',
            'data-placement':'top',
            'title':'Next'
        }
    )

    context = {
        'save_button': save_button,
        'edit_button': edit_button,
        'remove_button': remove_button,
        'previous_button': previous_button,
        'next_button': next_button
    }

    return render(request, 'hydroshare_python/home.html', context)

@login_required()
def loading(request):
    return render(request, 'hydroshare_python/loading.html')

@login_required()
def tutorial(request):
    """
    Controller for the app home page.
    """
    save_button = Button(
        display_text='',
        name='save-button',
        icon='glyphicon glyphicon-floppy-disk',
        style='success',
        attributes={
            'data-toggle':'tooltip',
            'data-placement':'top',
            'title':'Save'
        }
    )

    edit_button = Button(
        display_text='',
        name='edit-button',
        icon='glyphicon glyphicon-edit',
        style='warning',
        attributes={
            'data-toggle':'tooltip',
            'data-placement':'top',
            'title':'Edit'
        }
    )

    remove_button = Button(
        display_text='',
        name='remove-button',
        icon='glyphicon glyphicon-remove',
        style='danger',
        attributes={
            'data-toggle':'tooltip',
            'data-placement':'top',
            'title':'Remove'
        }
    )

    previous_button = Button(
        display_text='Previous',
        name='previous-button',
        attributes={
            'data-toggle':'tooltip',
            'data-placement':'top',
            'title':'Previous'
        }
    )

    next_button = Button(
        display_text='Next',
        name='next-button',
        attributes={
            'data-toggle':'tooltip',
            'data-placement':'top',
            'title':'Next'
        }
    )

    context = {
        'save_button': save_button,
        'edit_button': edit_button,
        'remove_button': remove_button,
        'previous_button': previous_button,
        'next_button': next_button
    }

    return render(request, 'hydroshare_python/tutorial.html', context)

@login_required()
def tethys(request):
    """
    Controller for the app home page.
    """
    save_button = Button(
        display_text='',
        name='save-button',
        icon='glyphicon glyphicon-floppy-disk',
        style='success',
        attributes={
            'data-toggle':'tooltip',
            'data-placement':'top',
            'title':'Save'
        }
    )

    edit_button = Button(
        display_text='',
        name='edit-button',
        icon='glyphicon glyphicon-edit',
        style='warning',
        attributes={
            'data-toggle':'tooltip',
            'data-placement':'top',
            'title':'Edit'
        }
    )

    remove_button = Button(
        display_text='',
        name='remove-button',
        icon='glyphicon glyphicon-remove',
        style='danger',
        attributes={
            'data-toggle':'tooltip',
            'data-placement':'top',
            'title':'Remove'
        }
    )

    previous_button = Button(
        display_text='Previous',
        name='previous-button',
        attributes={
            'data-toggle':'tooltip',
            'data-placement':'top',
            'title':'Previous'
        }
    )

    next_button = Button(
        display_text='Next',
        name='next-button',
        attributes={
            'data-toggle':'tooltip',
            'data-placement':'top',
            'title':'Next'
        }
    )

    context = {
        'save_button': save_button,
        'edit_button': edit_button,
        'remove_button': remove_button,
        'previous_button': previous_button,
        'next_button': next_button
    }

    return render(request, 'hydroshare_python/tethys.html', context)

@login_required()
def featurespage(request):
    """
    Controller for the app home page.
    """
    save_button = Button(
        display_text='',
        name='save-button',
        icon='glyphicon glyphicon-floppy-disk',
        style='success',
        attributes={
            'data-toggle':'tooltip',
            'data-placement':'top',
            'title':'Save'
        }
    )

    edit_button = Button(
        display_text='',
        name='edit-button',
        icon='glyphicon glyphicon-edit',
        style='warning',
        attributes={
            'data-toggle':'tooltip',
            'data-placement':'top',
            'title':'Edit'
        }
    )

    remove_button = Button(
        display_text='',
        name='remove-button',
        icon='glyphicon glyphicon-remove',
        style='danger',
        attributes={
            'data-toggle':'tooltip',
            'data-placement':'top',
            'title':'Remove'
        }
    )

    previous_button = Button(
        display_text='Previous',
        name='previous-button',
        attributes={
            'data-toggle':'tooltip',
            'data-placement':'top',
            'title':'Previous'
        }
    )

    next_button = Button(
        display_text='Next',
        name='next-button',
        attributes={
            'data-toggle':'tooltip',
            'data-placement':'top',
            'title':'Next'
        }
    )

    context = {
        'save_button': save_button,
        'edit_button': edit_button,
        'remove_button': remove_button,
        'previous_button': previous_button,
        'next_button': next_button
    }

    return render(request, 'hydroshare_python/featurespage.html', context)

@login_required()
def mapview(request):
    """
    Controller for the app home page.
    """
    username = ''
    password = ''
    resourcev=[]
    viewr = ''

    username_error = ''
    password_error = ''
    viewr_error = ''
    loggedin = False
    try:
            # pass in request object
        hs = get_oauth_hs(request)
        loggedin = True

    except Exception as e:
        pass
        # handle exceptions


    # Handle form submission
    print('POST REQUEST RECEIVED')
    if request.POST and not 'add-button' in request.POST:
        print('POST REQUEST STARTED')
        # Get values
        has_errors = False
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        viewr = request.POST.get('viewr', None)

            # Validate
        
        if not viewr:
            has_errors = True
            viewr_error = 'Subject is required.'
        try:
            # pass in request object
            hs = get_oauth_hs(request)

            # # your logic goes here. For example: list all HydroShare resources
            # for resource in hs.getResourceList():
            #     print(resource)

        except Exception as e:
        # handle exceptions

        
            if not username:
                has_errors = True
                username_error = 'Username is required.'
            
            elif not password:
                has_errors = True
                password_error = 'Password is required.'

            else:
                auth = HydroShareAuthBasic(username= username, password= password)
                hs = HydroShare(auth=auth)

        if not has_errors:
            # Do stuff here
            # hs.setAccessRules(public=True)
            result = hs.resources(subject=viewr)

            resourceList = []
            for resource in result:
                resourceList.append(resource)

            return HttpResponse(json.dumps(resourceList))
            # return {"status": success }

        if has_errors:    
        #Utah Municipal resource id
            messages.error(request, "Please fix errors.")

    username_input = TextInput(
        display_text='Username',
        name='username',
        placeholder='Enter your username'
    )

    password_input = TextInput(
        display_text='Password',
        name='password',
        attributes={"type":"password"},
        placeholder='Enter your password'
    )

    viewr_input = TextInput(
        display_text='Subject',
        name='viewr',
        placeholder='Enter your subject'
    )

    add_button = Button(
        display_text='View on Map',
        name='add-button',
        icon='glyphicon glyphicon-plus',
        style='success',
        attributes={'form': 'add-dam-form'},
        submit=True
    )

    cancel_button = Button(
        display_text='Cancel',
        name='cancel-button',
        href=reverse('hydroshare_python:home')
    )

    context = {
        'loggedin' : loggedin,
        'username_input': username_input,
        'password_input': password_input,
        'viewr_input': viewr_input,
        'add_button': add_button,
        'cancel_button': cancel_button,
        'resourcev': resourcev,
    }

    return render(request, 'hydroshare_python/mapview.html', context)

@login_required()
def boundingbox(request):
    """
    Controller for the app home page.
    """
    username = ''
    password = ''
    resourcev=[]
    viewr = ''

    username_error = ''
    password_error = ''
    viewr_error = ''
    loggedin = False
    try:
            # pass in request object
        hs = get_oauth_hs(request)
        loggedin = True

    except Exception as e:
        pass

    # Handle form submission
    print('POST REQUEST RECEIVED')
    if request.POST and not 'add-button' in request.POST:
        print('POST REQUEST STARTED')
        # Get values
        has_errors = False
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        viewr = request.POST.get('viewr', None)

            # Validate
        if not viewr:
            has_errors = True
            viewr_error = 'Subject is required.'

        try:
            # pass in request object
            hs = get_oauth_hs(request)

            # # your logic goes here. For example: list all HydroShare resources
            # for resource in hs.getResourceList():
            #     print(resource)

        except Exception as e:
        # handle exceptions

        
            if not username:
                has_errors = True
                username_error = 'Username is required.'
            
            elif not password:
                has_errors = True
                password_error = 'Password is required.'

            else:
                auth = HydroShareAuthBasic(username= username, password= password)
                hs = HydroShare(auth=auth)

        if not has_errors:
            # Do stuff here
            # auth = HydroShareAuthBasic(username= username, password= password)
            # hs = HydroShare(auth=auth)
            # hs.setAccessRules(public=True)
            result = hs.resources(subject=viewr)

            resourceList = []
            for resource in result:
                resourceList.append(resource)

            return HttpResponse(json.dumps(resourceList))
            # return {"status": success }

        if has_errors:    
        #Utah Municipal resource id
            messages.error(request, "Please fix errors.")

    username_input = TextInput(
        display_text='Username',
        name='username',
        placeholder='Enter your username'
    )

    password_input = TextInput(
        display_text='Password',
        name='password',
        attributes={"type":"password"},
        placeholder='Enter your password'
    )

    viewr_input = TextInput(
        display_text='Subject',
        name='viewr',
        placeholder='Enter your subject'
    )

    add_button = Button(
        display_text='View on Map',
        name='add-button',
        icon='glyphicon glyphicon-plus',
        style='success',
        attributes={'form': 'add-dam-form'},
        submit=True
    )

    cancel_button = Button(
        display_text='Cancel',
        name='cancel-button',
        href=reverse('hydroshare_python:home')
    )

    context = {
        'loggedin' : loggedin,
        'username_input': username_input,
        'password_input': password_input,
        'viewr_input': viewr_input,
        'add_button': add_button,
        'cancel_button': cancel_button,
        'resourcev': resourcev,
    }

    return render(request, 'hydroshare_python/boundingbox.html', context)

def filtershapefile(in_num):

    return in_num['file_name'].endswith('.shp') and in_num["logical_file_type"]=="GeoFeatureLogicalFile"

@login_required()
def random(request):
    """
    Controller for the app home page.
    """
    # username = ''
    # password = ''
    
    # title = 'nyu_2451_34514'
    resource = request.GET.get('id','')
    resourceid = 'HS-'+resource
            
    auth = HydroShareAuthBasic(username= 'abhishekamal18@gmail.com', password= 'hydro1234')
    hs = HydroShare(auth=auth)
    resource_md = hs.getSystemMetadata(resource)
    print(resource_md)
    # title = resource_md['title']
    bb1=resource_md['coverages'][0]['value']['northlimit']
    bb2=resource_md['coverages'][0]['value']['eastlimit']
    bb3=resource_md['coverages'][0]['value']['southlimit']
    bb4=resource_md['coverages'][0]['value']['westlimit']
    resourcefiles=hs.resource(resource).files.all().content

    print(resourcefiles)
    
    try:


# Demonstrating filter() to remove odd numbers
        out_filter = filter(filtershapefile, json.loads(resourcefiles.decode('utf-8'))['results'])
        # print(next(out_filter))
        title=next(out_filter,None)['url'].replace('.shp','')
        titleindex=title.index('data/contents/')
        title=title[title.find('data/contents/'):].replace('data/contents/','').replace('/',' ')

    except:
        title = " "

    context = {
        'bb1':bb1,
        'bb2':bb2,
        'bb3':bb3,
        'bb4':bb4,
        'resourceid':resourceid,
        'title':title,
        
    }

    return render(request, 'hydroshare_python/random.html', context)

@login_required()
def geoserver(request):
    """
    Controller for the app home page.
    """
    username = ''
    password = ''
    resourcev=[]
    viewr = ''
    bb1 = ''
    bb2 = ''
    bb3 = ''
    resourceid = ''

    username_error = ''
    password_error = ''
    viewr_error = ''
    bb1_error = ''
    bb2_error = ''
    bb3_error = ''
    bb4_error = ''
    resourceid_error = ''
    loggedin = False
    try:
            # pass in request object
        hs = get_oauth_hs(request)
        loggedin = True

    except Exception as e:
        pass

    # Handle form submission
    print('POST REQUEST RECEIVED')
    if request.POST and not 'add-button' in request.POST:
        print('POST REQUEST STARTED')
        # Get values
        has_errors = False
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        viewr = request.POST.get('viewr', None)
        bb1 = request.POST.get('bb1', None)
        bb2 = request.POST.get('bb2', None)
        bb3 = request.POST.get('bb3', None)
        bb4 = request.POST.get('bb4', None)
        resourceid_error = request.POST.get('resourceid', None)
            # Validate
        
        if not viewr:
            has_errors = True
            viewr_error = 'Subject is required.'
            
        try:
            # pass in request object
            hs = get_oauth_hs(request)

            # # your logic goes here. For example: list all HydroShare resources
            # for resource in hs.getResourceList():
            #     print(resource)

        except Exception as e:
        # handle exceptions

        
            if not username:
                has_errors = True
                username_error = 'Username is required.'
            
            elif not password:
                has_errors = True
                password_error = 'Password is required.'

            else:
                auth = HydroShareAuthBasic(username= username, password= password)
                hs = HydroShare(auth=auth)

        if not bb1:
            has_errors = True
            bb1_error = 'bb1 is required.'

        if not bb2:
            has_errors = True
            bb2_error = 'bb2 is required.'

        if not bb3:
            has_errors = True
            bb3_error = 'bb3 is required.'

        if not bb4:
            has_errors = True
            bb4_error = 'bb4 is required.'

        if not resourceid:
            has_errors = True
            resourceid_error = 'resourceid is required.'


        if not has_errors:
            # Do stuff here
            # auth = HydroShareAuthBasic(username= username, password= password)
            # hs = HydroShare(auth=auth)
            # hs.setAccessRules(public=True)
            result = hs.resources(subject=viewr)

            resourceList = []
            for resource in result:
                resourceList.append(resource)

            return HttpResponse(json.dumps(resourceList))
            # return {"status": success }

        if has_errors:    
        #Utah Municipal resource id
            messages.error(request, "Please fix errors.")

    username_input = TextInput(
        display_text='Username',
        name='username',
        placeholder='Enter your username'
    )

    password_input = TextInput(
        display_text='Password',
        name='password',
        attributes={"type":"password"},
        placeholder='Enter your password'
    )

    bb1_input = TextInput(
        display_text='bb1',
        name='bb1',
        placeholder='Enter your bounding box co-ordinate 1'
    )
    bb2_input = TextInput(
        display_text='bb2',
        name='bb2',
        placeholder='Enter your bounding box co-ordinate 2'
    )
    bb3_input = TextInput(
        display_text='bb3',
        name='bb3',
        placeholder='Enter your bounding box co-ordinate 3'
    )
    bb4_input = TextInput(
        display_text='bb4',
        name='bb4',
        placeholder='Enter your bounding box co-ordinate 4'
    )
    resourceid_input = TextInput(
        display_text='Resource ID',
        name='resourceid',
        placeholder='Enter the resource id'
    )

     
    add_button = Button(
        display_text='View on Map',
        name='add-button',
        icon='glyphicon glyphicon-plus',
        style='success',
        attributes={'form': 'add-dam-form'},
        submit=True
    )

    cancel_button = Button(
        display_text='Cancel',
        name='cancel-button',
        href=reverse('hydroshare_python:home')
    )

    context = {
        'loggedin' : loggedin,
        'bb1_input':bb1_input,
        'bb2_input':bb2_input,
        'bb3_input':bb3_input,
        'bb4_input':bb4_input,
        'resourceid_input':resourceid_input,
        'username_input': username_input,
        'password_input': password_input,
        'add_button': add_button,
        'cancel_button': cancel_button,
        'resourcev': resourcev,
    }

    return render(request, 'hydroshare_python/geoserver.html', context)



@login_required()
def get_file(request):
    """
    Controller for the Add Dam page.
    """
    # Default Values
    title = ''
    owner = 'Reclamation'
    username = ''
    password = ''
    # river = ''
    date_built = ''
    author = ''

    

    # Errors
    title_error = ''
    owner_error = ''
    username_error = ''
    password_error = ''
    # river_error = ''
    date_error = ''
    author_error = ''
    loggedin = False
    try:
            # pass in request object
        hs = get_oauth_hs(request)
        loggedin = True

    except Exception as e:
        pass


    # Handle form submission
    if request.POST and 'create-button' in request.POST:
        # Get values
        has_errors = False
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        owner = request.POST.get('owner', None)
        # river = request.POST.get('river', None)
        date_built = request.POST.get('date-built', None)
        author = request.POST.get('author', None)
        coauthor = author.split(',')
        authorsObj = ""
        for i, author in enumerate(coauthor):
            separator = ',' if i>0 else ''
            authorsObj = authorsObj + separator + '{"creator":{"name":"'+author.strip()+'"}}'
        title = request.POST.get('title', None)
        print(dict(request.FILES))
        uploaded_file = request.FILES['uploadedfile']
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_zip_path = os.path.join(temp_dir, uploaded_file.name)
            print(temp_zip_path)

            # Use with statements to ensure opened files are closed when done
            with open(temp_zip_path, 'wb') as temp_zip:
                for chunk in uploaded_file.chunks():
                    temp_zip.write(chunk)

            # Validate
            if not title:
                has_errors = True
                title_error = 'Title is required.'

            if not owner:
                has_errors = True
                owner_error = 'Owner is required.'

            try:
            # pass in request object
                hs = get_oauth_hs(request)

            # your logic goes here. For example: list all HydroShare resources
                # for resource in hs.getResourceList():
                #     print(resource)

            except Exception as e:
        # handle exceptions
            
                if not username:
                    has_errors = True
                    username_error = 'Username is required.'
                
                elif not password:
                    has_errors = True
                    password_error = 'Password is required.'

                else:
                    auth = HydroShareAuthBasic(username= username, password= password)
                    hs = HydroShare(auth=auth)

            if not date_built:
                has_errors = True
                date_error = 'Date Built is required.'

            if not author:
                has_errors = True
                river_error = 'Author is required.'

            if not has_errors: 
                # auth = HydroShareAuthBasic(username= username, password= password)
                # hs = HydroShare(auth=auth)
                abstract = date_built
                keywords = owner.split(', ')
                rtype = 'GenericResource'
                fpath = temp_zip_path #fpath = 'tethysapp/geocode/workspaces/app_workspace/output.txt'
                metadata = '[{"coverage":{"type":"period", "value":{"start":"01/01/2000", "end":"12/12/2010"}}}, '+authorsObj+']'
                extra_metadata = '{"key-1": "value-1", "key-2": "value-2"}'
                resource_id = hs.createResource(rtype, title, resource_file=fpath, keywords=keywords, abstract=abstract, metadata=metadata, extra_metadata=extra_metadata)
                messages.success(request, "Resource created successfully")
                # return {"status": success }
            if has_errors:    
            #Utah Municipal resource id
                messages.error(request, "Please fix errors.")

    # Define form gizmos
    title_input = TextInput(
        display_text='Title',
        name='title',
        placeholder= 'Enter the name of your resource'
    )

    owner_input = TextInput(
        display_text='Keywords',
        name='owner',
        placeholder='eg: shapefiles, datasets, etc..'
    )

    username_input = TextInput(
        display_text='Username',
        name='username',
        placeholder='Enter your username'
    )

    password_input = TextInput(
        display_text='Password',
        name='password',
        attributes={"type":"password"},
        placeholder='Enter your password'
    ) 

    # river_input = TextInput(
    #     display_text='Name of Creator',
    #     name='river',
    #     placeholder='e.g: John Smith'
    # )

    date_built = TextInput(
        display_text='Abstract',
        name='date-built',
        placeholder='Type in your abstract here'
    
    )

    author_input = TextInput(
        display_text='Author/Co-authors',
        name='author',
        placeholder='Enter the name of the Author and Co-authors'
    )

    create_button = Button(
        display_text='Create',
        name='create-button',
        icon='glyphicon glyphicon-plus',
        style='success',
        attributes={'form': 'add-dam-form'},
        submit=True
    )

    cancel_button = Button(
        display_text='Cancel',
        name='cancel-button',
        href=reverse('hydroshare_python:home')
    )

    context = {
        'loggedin' : loggedin,
        'title_input': title_input,
        'owner_input': owner_input,
        'username_input': username_input,
        'password_input': password_input,
        'date_built_input': date_built,
        'author_input': author_input,
        'create_button': create_button,
        'cancel_button': cancel_button,
    }

    return render(request, 'hydroshare_python/get_file.html', context)

@login_required()
def add_file(request):
    """
    Controller for the Add Dam page.
    """
    # Default Values
    username = ''
    password = ''
    resourcein = ''
    

    # Errors
    username_error = ''
    password_error = ''
    resourcein_error = ''
    loggedin = False
    try:
            # pass in request object
        hs = get_oauth_hs(request)
        loggedin = True

    except Exception as e:
        pass
        # handle exceptions

    # Handle form submission
    if request.POST and 'add-button' in request.POST:
        # Get values
        has_errors = False
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        resourcein = request.POST.get('resourcein', None)
        print(dict(request.FILES))
        uploaded_file = request.FILES['addfile']

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_zip_path = os.path.join(temp_dir, uploaded_file.name)
            print(temp_zip_path)

            # Use with statements to ensure opened files are closed when done
            with open(temp_zip_path, 'wb') as temp_zip:
                for chunk in uploaded_file.chunks():
                    temp_zip.write(chunk)

            # Validate
            try:
            # pass in request object
                hs = get_oauth_hs(request)

                # your logic goes here. For example: list all HydroShare resources
                # for resource in hs.getResourceList():
                #     print(resource)

            except Exception as e:
            # handle exceptions
                if not username:
                    has_errors = True
                    username_error = 'Username is required.'
                
                elif not password:
                    has_errors = True
                    password_error = 'Password is required.'

                else:
                    auth = HydroShareAuthBasic(username= username, password= password)
                    hs = HydroShare(auth=auth)
            
            if not resourcein:
                has_errors = True
                resourcein_error = 'Resource is required.'


            if not has_errors:
                fpath = temp_zip_path 
                resource_id = hs.addResourceFile(resourcein, fpath) 
                messages.success(request, "File added successfully")
            if has_errors:
                messages.error(request, "Please fix errors.")

    # Define form gizmos
    resourcein_input = TextInput(
        display_text='Resource ID',
        name='resourcein',
        placeholder='Enter id here eg: 08c6e88adaa647cd9bb28e5d619178e0 '
    )

    username_input = TextInput(
        display_text='Username',
        name='username',
        placeholder='Enter your username'
    )

    password_input = TextInput(
        display_text='Password',
        name='password',
        attributes={"type":"password"},
        placeholder='Enter your password'
    ) 

    add_button = Button(
        display_text='Add',
        name='add-button',
        icon='glyphicon glyphicon-plus',
        style='success',
        attributes={'form': 'add-dam-form'},
        submit=True
    )

    cancel_button = Button(
        display_text='Cancel',
        name='cancel-button',
        href=reverse('hydroshare_python:home')
    )

    context = {
        'loggedin' : loggedin,
        'resourcein_input': resourcein_input,
        'username_input': username_input,
        'password_input': password_input,
        'add_button': add_button,
        'cancel_button': cancel_button,
    }

    return render(request, 'hydroshare_python/add_file.html', context)

@login_required()
def delete_resource(request):
    """
    Controller for the Add Dam page.
    """
    # Default Values
    username = ''
    password = ''
    # filename = ''
    resourcein = ''
    # owner = 'Reclamation'
    # river = ''
    # date_built = ''

    # Errors
    username_error = ''
    password_error = ''
    # filename_error = ''
    resourcein_error = ''
    # owner_error = ''
    # river_error = ''
    # date_error = ''
    loggedin = False
    try:
            # pass in request object
        hs = get_oauth_hs(request)
        loggedin = True

    except Exception as e:
        pass
        # handle exceptions

    # Handle form submission
    if request.POST and 'delete-button' in request.POST:
        # Get values
        has_errors = False
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        resourcein = request.POST.get('resourcein', None)
        

        # Validate

        if not resourcein:
            has_errors = True
            resourcein_error = 'Resource ID is required.'

        try:
            # pass in request object
            hs = get_oauth_hs(request)

            # your logic goes here. For example: list all HydroShare resources
            # for resource in hs.getResourceList():
            #     print(resource)

        except Exception as e:
        # handle exceptions

        
            if not username:
                has_errors = True
                username_error = 'Username is required.'
            
            elif not password:
                has_errors = True
                password_error = 'Password is required.'

            else:
                auth = HydroShareAuthBasic(username= username, password= password)
                hs = HydroShare(auth=auth)
        # if not river:
        #     has_errors = True
        #     river_error = 'River is required.'



        if not has_errors:
            # Do stuff here
            hs.deleteResource(resourcein)
            messages.success(request, "Resource deleted successfully")
        if has_errors:    
            messages.error(request, "Please fix errors.")

        

    # Define form gizmos
    resourcein_input = TextInput(
        display_text='Resource ID',
        name='resourcein',
        placeholder='Enter the Resource ID here'
    )

    username_input = TextInput(
        display_text='Username',
        name='username',
        placeholder='Enter your username'
    )

    password_input = TextInput(
        display_text='Password',
        name='password',
        attributes={"type":"password"},
        placeholder='Enter your password'
    ) 


    delete_button = Button(
        display_text='Delete Resource',
        name='delete-button',
        icon='glyphicon glyphicon-plus',
        style='success',
        attributes={'form': 'add-dam-form'},
        submit=True
    )

    cancel_button = Button(
        display_text='Cancel',
        name='cancel-button',
        href=reverse('hydroshare_python:home')
    )

    context = {
        'loggedin' : loggedin,
        'resourcein_input': resourcein_input,
        'username_input': username_input,
        'password_input': password_input,
        'delete_button': delete_button,
        'cancel_button': cancel_button

    }

    return render(request, 'hydroshare_python/delete_resource.html', context)

@login_required()
def filev(request):
    """
    Controller for the Add Dam page.
    """
    # Default Values
    # filename = ''
    username = ''
    password = ''
    resourcein = ''
    # owner = 'Reclamation'
    # river = ''
    # date_built = ''

    # Errors
    title_error = ''
    # filename_error = ''
    resourcein_error = ''
    username_error = ''
    password_error = ''
    # date_error = ''
    

    # Handle form submission
    if request.POST:
        # Get values
        has_errors = False
        # filename = request.POST.get('filename', None)
        resourcein = request.POST.get('resourcein', None)
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        
        # Validate

        if not resourcein:
            has_errors = True
            resourcein_error = 'Resource ID is required.'

        try:
            # pass in request object
            hs = get_oauth_hs(request)

        except Exception as e:
        
            if not username:
                has_errors = True
                username_error = 'Username is required.'
            
            elif not password:
                has_errors = True
                password_error = 'Password is required.'

            else:
                auth = HydroShareAuthBasic(username= username, password= password)
                hs = HydroShare(auth=auth)

        # if not river:
        #     has_errors = True
        #     river_error = 'River is required.'

        if not has_errors:
            # Do stuff here
            # auth = HydroShareAuthBasic(username= username, password= password)
            # hs = HydroShare(auth=auth)
            resourcefiles=hs.resource(resourcein).files.all().content
            return HttpResponse(resourcefiles)

        return HttpResponse('')

@login_required()
def download_file(request):
    """
    Controller for the Add Dam page.
    """
    # Default Values
    title = ''
    # filename = ''
    username = ''
    password = ''
    resourcein = ''
    filev = []
    # owner = 'Reclamation'
    # river = ''
    # date_built = ''

    # Errors
    title_error = ''
    # filename_error = ''
    resourcein_error = ''
    username_error = ''
    password_error = ''
    # date_error = ''
    loggedin = False
    try:
            # pass in request object
        hs = get_oauth_hs(request)
        loggedin = True

    except Exception as e:
        pass

    # Handle form submission
    if request.POST and 'download-button' in request.POST:
        # Get values
        has_errors = False
        # filename = request.POST.get('filename', None)
        resourcein = request.POST.get('resourcein', None)
        title = request.POST.get('title_input', None)
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        
        
        # Validate

        if not resourcein:
            has_errors = True
            resourcein_error = 'Resource ID is required.'

        if not title:
            has_errors = True
            title_error = 'Title is required.'
        
        try:
            # pass in request object
            hs = get_oauth_hs(request)

            # your logic goes here. For example: list all HydroShare resources
            # for resource in hs.getResourceList():
            #     print(resource)

        except Exception as e:
        # handle exceptions

        
            if not username:
                has_errors = True
                username_error = 'Username is required.'
            
            elif not password:
                has_errors = True
                password_error = 'Password is required.'

            else:
                auth = HydroShareAuthBasic(username= username, password= password)
                hs = HydroShare(auth=auth)

        # if not river:
        #     has_errors = True
        #     river_error = 'River is required.'

        if not has_errors:
            # Do stuff here
            # auth = HydroShareAuthBasic(username= username, password= password)
            # hs = HydroShare(auth=auth)
            fname = title
            fpath = hs.getResourceFile(resourcein, fname, destination= '/tmp')
            # response = HttpResponse( content_type='application/force-download')
            # response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(fname)
            # response['X-Sendfile'] = smart_str('/tmp')
            # return response
            fpath='/tmp/%s' % title
            #hs.getResource(title, destination='/tmp')
            # response = HttpResponse( content_type='application/force-download')
            # response['Content-Disposition'] = 'attachment; filename=%s.zip' % smart_str(title)
            # response['X-Sendfile'] = smart_str('/tmp')
            # response['Content-Length'] = os.path.getsize(fpath)
            # print(os.path.getsize(fpath))

            wrapper = FileWrapper(open(os.path.abspath(fpath), 'rb')) 
            response = HttpResponse(wrapper, content_type='text/plain') 
            response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(fpath) 
            response['Content-Length'] = os.path.getsize(fpath)
            return response
        if has_errors:    
                #Utah Municipal resource id
            messages.error(request, "Please fix errors.")

    # Define form gizmos
    resourcein_input = TextInput(
        display_text='Resource ID',
        name='resourcein'
    )

    title_input = TextInput(
        display_text='Name of the file you want to download including the extension',
        name='title',
        placeholder='eg: filename.shp or filename.txt'
    )

    username_input = TextInput(
        display_text='Username',
        name='username',
        placeholder='Enter your username'
    )

    password_input = TextInput(
        display_text='Password',
        name='password',
        attributes={"type":"password"},
        placeholder='Enter your password'
    ) 


    add_button = Button(
        display_text='Download',
        name='download-button',
        icon='glyphicon glyphicon-plus',
        style='success',
        attributes={'form': 'add-dam-form'},
        submit=True
    )

    cancel_button = Button(
        display_text='Cancel',
        name='cancel-button',
        href=reverse('hydroshare_python:home')
    )

    context = {
        'loggedin' : loggedin,
        'resourcein_input': resourcein_input,
        'title_input': title_input,
        'username_input': username_input,
        'password_input': password_input,
        'add_button': add_button,
        'cancel_button': cancel_button,
        'filev':filev

    }

    return render(request, 'hydroshare_python/download_file.html', context)


@login_required()
def delete_file(request):
    """
    Controller for the Add Dam page.
    """
    # Default Values
    title = ''
    # filename = ''
    username = ''
    password = ''
    resourcein = ''
    filev = []
    # owner = 'Reclamation'
    # river = ''
    # date_built = ''

    # Errors
    title_error = ''
    # filename_error = ''
    resourcein_error = ''
    username_error = ''
    password_error = ''
    # date_error = ''
    loggedin = False
    try:
            # pass in request object
        hs = get_oauth_hs(request)
        loggedin = True

    except Exception as e:
        pass
        # handle exceptions

    # Handle form submission
    if request.POST and 'delete-button' in request.POST:
        # Get values
        has_errors = False
        # filename = request.POST.get('filename', None)
        resourcein = request.POST.get('resourcein', None)
        title = request.POST.get('title_input', None)
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        

        # Validate

        if not resourcein:
            has_errors = True
            resourcein_error = 'Resource ID is required.'

        try:
            # pass in request object
            hs = get_oauth_hs(request)

            # your logic goes here. For example: list all HydroShare resources
            # for resource in hs.getResourceList():
            #     print(resource)

        except Exception as e:
        # handle exceptions

        
            if not username:
                has_errors = True
                username_error = 'Username is required.'
            
            elif not password:
                has_errors = True
                password_error = 'Password is required.'

            else:
                auth = HydroShareAuthBasic(username= username, password= password)
                hs = HydroShare(auth=auth)

        # if not river:
        #     has_errors = True
        #     river_error = 'River is required.'

        if not has_errors:
            # Do stuff here
            # auth = HydroShareAuthBasic(username= username, password= password)
            # hs = HydroShare(auth=auth)
            resource_id = hs.deleteResourceFile(resourcein, title)
            messages.success(request, "File deleted successfully")
        if has_errors:    
                #Utah Municipal resource id
            messages.error(request, "Please fix errors.")

        

    # Define form gizmos
    resourcein_input = TextInput(
        display_text='Resource ID',
        name='resourcein',
        placeholder='Enter the Resource ID here'
    )


    username_input = TextInput(
        display_text='Username',
        name='username',
        placeholder='Enter your username'
    )

    password_input = TextInput(
        display_text='Password',
        name='password',
        attributes={"type":"password"},
        placeholder='Enter your password'
    ) 


    delete_button = Button(
        display_text='Delete File',
        name='delete-button',
        icon='glyphicon glyphicon-plus',
        style='success',
        attributes={'form': 'add-dam-form'},
        submit=True
    )

    cancel_button = Button(
        display_text='Cancel',
        name='cancel-button',
        href=reverse('hydroshare_python:home')
    )

    context = {
        'loggedin' : loggedin,
        'resourcein_input': resourcein_input,
        'username_input': username_input,
        'password_input': password_input,
        'delete_button': delete_button,
        'cancel_button': cancel_button,
        'filev': filev

    }

    return render(request, 'hydroshare_python/delete_file.html', context)

@login_required()
def getfile_metadata(request):
    """
    Controller for the Add Dam page.
    """
    # Default Values
    title = ''
    # filename = ''
    username = ''
    password = ''
    resourcein = ''
    filev = []
    # owner = 'Reclamation'
    # river = ''
    # date_built = ''

    # Errors
    title_error = ''
    # filename_error = ''
    resourcein_error = ''
    username_error = ''
    password_error = ''
    loggedin = False
    try:
            # pass in request object
        hs = get_oauth_hs(request)
        loggedin = True

    except Exception as e:
        pass
        # handle exceptions
    # date_error = ''

    # Handle form submission
    if request.POST:
        # Get values
        has_errors = False
        # filename = request.POST.get('filename', None)
        resourcein = request.POST.get('resourcein', None)
        title = request.POST.get('title_input', None)
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        
        
        # Validate

        if not resourcein:
            has_errors = True
            resourcein_error = 'Resource ID is required.'

        if not title:
            has_errors = True
            title_error = 'Title is required.'
        
        try:
            # pass in request object
            hs = get_oauth_hs(request)

        # # your logic goes here. For example: list all HydroShare resources
        #     for resource in hs.getResourceList():
        #         print(resource)

        except Exception as e:
    # handle exceptions
        
            if not username:
                has_errors = True
                username_error = 'Username is required.'
            
            elif not password:
                has_errors = True
                password_error = 'Password is required.'

            else:
                auth = HydroShareAuthBasic(username= username, password= password)
                hs = HydroShare(auth=auth)

        # if not river:
        #     has_errors = True
        #     river_error = 'River is required.'

        if not has_errors:
            # Do stuff here
            # auth = HydroShareAuthBasic(username= username, password= password)
            # hs = HydroShare(auth=auth)
            response = hs.resource(resourcein).files.metadata(title).content
            
            # response_serialized = serializers.serialize('json', response)

            return HttpResponse(response.decode("utf-8"))
            # return JsonResponse(response_serialized, safe=False)
             
        if has_errors:    
                #Utah Municipal resource id
            messages.error(request, "Please fix errors.")

    # Define form gizmos
    resourcein_input = TextInput(
        display_text='Resource ID',
        name='resourcein'
    )

    title_input = TextInput(
        display_text='Name of the file you want to download including the extension',
        name='title',
        placeholder='eg: filename.shp or filename.txt'
    )

    username_input = TextInput(
        display_text='Username',
        name='username',
        placeholder='Enter your username'
    )

    password_input = TextInput(
        display_text='Password',
        name='password',
        attributes={"type":"password"},
        placeholder='Enter your password'
    ) 


    add_button = Button(
        display_text='Download',
        name='download-button',
        icon='glyphicon glyphicon-plus',
        style='success',
        attributes={'form': 'add-dam-form'},
        submit=True
    )

    cancel_button = Button(
        display_text='Cancel',
        name='cancel-button',
        href=reverse('hydroshare_python:home')
    )

    context = {
        'loggedin' : loggedin,
        'resourcein_input': resourcein_input,
        'title_input': title_input,
        'username_input': username_input,
        'password_input': password_input,
        'add_button': add_button,
        'cancel_button': cancel_button,
        'filev':filev

    }

    return render(request, 'hydroshare_python/getfile_metadata.html', context)

@login_required()
def metadata(request):
    """
    Controller for the Add Dam page.
    """
    # Default Values
    username = ''
    password = ''
    creator1= ''
    creator2= ''
    organization= ''
    Email=''
    Address=''
    Phone=''
    detail1=''
    detail2=''
    # filename = ''
    resourcein = ''
    # owner = 'Reclamation'
    # river = ''
    # date_built = ''

    # Errors
    username_error = ''
    password_error = ''
    # filename_error = ''
    resourcein_error = ''
    creator1_error = ''
    creator2_error = ''
    organization_error = ''
    Email_error =''
    Address_error =''
    Phone_error =''
    detail1_error =''
    detail2_error =''
    loggedin = False
    try:
            # pass in request object
        hs = get_oauth_hs(request)
        loggedin = True

    except Exception as e:
        pass
    # owner_error = ''
    # river_error = ''
    # date_error = ''

    # Handle form submission
    if request.POST and 'add-button' in request.POST:
        # Get values
        has_errors = False
        # filename = request.POST.get('filename', None)
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        creator1 = request.POST.get('creator1', None)
        creator2 = request.POST.get('creator2', None)
        coauthor = creator2.split(',')
        organization = request.POST.get('organization', None)
        Email = request.POST.get('Email', None)
        Address = request.POST.get('Address', None)
        Phone = request.POST.get('Phone', None)
        detail1 = request.POST.get('detail1', None)
        detail2 = request.POST.get('detail2', None)
        resourcein = request.POST.get('resourcein', None)

        # Validate
        if not creator1:
            has_errors = True
            password_error = 'creator1 is required.'

        
        try:
        # pass in request object
            hs = get_oauth_hs(request)

        # your logic goes here. For example: list all HydroShare resources
            # for resource in hs.getResourceList():
            #     print(resource)

        except Exception as e:
    # handle exceptions
        
            if not username:
                has_errors = True
                username_error = 'Username is required.'
            
            elif not password:
                has_errors = True
                password_error = 'Password is required.'

            else:
                auth = HydroShareAuthBasic(username= username, password= password)
                hs = HydroShare(auth=auth)


        if not organization:
            has_errors = True
            password_error = 'organization is required.'

        if not Email:
            has_errors = True
            password_error = 'Email is required.'

        if not Address:
            has_errors = True
            password_error = 'Address is required.'

        if not Phone:
            has_errors = True
            password_error = 'Phone is required.'

        if not detail1:
            has_errors = True
            password_error = 'detail1 is required.'

        if not detail2:
            has_errors = True
            password_error = 'detail2 is required.'
        
        if not resourcein:
            has_errors = True
            resourcein_error = 'Resource is required.'

        # if not filename:
        #     has_errors = True
        #     filename_error = 'Filename is required.'

        if not has_errors:
            # Do stuff here
            # title = title
            # filename = filename
            # auth = HydroShareAuthBasic(username= username, password= password)
            # hs = HydroShare(auth=auth)
            print(creator1)
            metadata = {
                "coverages": [
                    {"type": "period", "value": {"start": detail1, "end": detail2}}
                ],
                "creators": [
                    {"name": creator1 , "organization": organization , "email": Email , "address": Address , "phone": Phone},
                ]
            }

            for i, author in enumerate(coauthor):
                metadata["creators"].append({ "name": author.strip() })

            print(metadata)
            science_metadata_json = hs.updateScienceMetadata(resourcein, metadata=metadata)
            messages.success(request, "Metadata added successfully")
        if has_errors:
            messages.error(request, "Please fix errors.")

    # Define form gizmos
    resourcein_input = TextInput(
        display_text='Resource ID',
        name='resourcein',
        placeholder='Enter id here eg: 08c6e88adaa647cd9bb28e5d619178e0 '
    )

    username_input = TextInput(
        display_text='Username',
        name='username',
        placeholder='Enter your username'
    )

    password_input = TextInput(
        display_text='Password',
        name='password',
        attributes={"type":"password"},
        placeholder='Enter your password'
    )

    creator1_input = TextInput(
        display_text='Author(s) and/ or Chief Contributor(s)',
        name='creator1',
        placeholder='Enter the name of the Author(s) and/ or Chief Contributor(s)'
    )

    creator2_input = TextInput(
        display_text='Co-authors',
        name='creator2',
        placeholder='Enter the name of other contributors to the resource'
    )

    organization_input = TextInput(
        display_text='Organization',
        name='organization',
        placeholder='Enter your organization'
    )

    Email_input = TextInput(
        display_text='Email',
        name='Email',
        placeholder='Enter your Email'
    )

    Address_input = TextInput(
        display_text='Address',
        name='Address',
        placeholder='Enter your Address'
    )

    Phone_input = TextInput(
        display_text='Phone',
        name='Phone',
        placeholder='Enter your Phone'
    )

    detail1_input = DatePicker(
        name='detail1',
        display_text='Date Built',
        autoclose=True,
        format='MM d, yyyy',
        start_view='decade',
        today_button=True,
        initial=detail1,
        error=detail1_error
    )

    detail2_input = DatePicker(
        name='detail2',
        display_text='Date Built',
        autoclose=True,
        format='MM d, yyyy',
        start_view='decade',
        today_button=True,
        initial=detail2,
        error=detail2_error
    )

    # filename_input = TextInput(
    #     display_text='File name',
    #     name='title',
    #     placeholder='Enter the name of file here '
    # )

    # owner_input = TextInput(
    #     display_text='Keywords',
    #     name='owner',
    #     placeholder='eg: shapefiles, datasets, etc..'
    # ) 

    # river_input = TextInput(
    #     display_text='Name of Creator',
    #     name='river',
    #     placeholder='e.g: John Smith'
    # )

    # date_built = TextInput(
    #     display_text='Keywords',
    #     name='date-built',
    #     placeholder='e.g: Shapefiles, datasets, etc..'
    
    # )

    add_button = Button(
        display_text='Submit',
        name='add-button',
        icon='glyphicon glyphicon-plus',
        style='success',
        attributes={'form': 'add-dam-form'},
        submit=True
    )

    cancel_button = Button(
        display_text='Cancel',
        name='cancel-button',
        href=reverse('hydroshare_python:home')
    )

    context = {
        'loggedin' : loggedin,
        'resourcein_input': resourcein_input,
        'username_input': username_input,
        'password_input': password_input,
        'creator1_input': creator1_input,
        'creator2_input': creator2_input,
        'organization_input': organization_input,
        'Email_input': Email_input,
        'Address_input': Address_input,
        'Phone_input': Phone_input,
        'detail1_input': detail1_input,
        'detail2_input': detail2_input,
        # 'filename_input': filename_input,
        # 'owner_input': owner_input,
        # 'river_input': river_input,
        # 'date_built_input': date_built,
        'add_button': add_button,
        'cancel_button': cancel_button,
    }

    return render(request, 'hydroshare_python/metadata.html', context)

@login_required()
def viewer(request):
    """
    Controller for the Add Dam page.
    """
    # Default Values
    
    username = ''
    password = ''
    resourcev=[]
    viewr = ''
    

    # Errors
    username_error = ''
    password_error = ''
    viewr_error = ''
    loggedin = False
    try:
            # pass in request object
        hs = get_oauth_hs(request)
        loggedin = True

    except Exception as e:
        pass


    # Handle form submission
    print('POST REQUEST RECEIVED')
    if request.POST and not 'add-button' in request.POST:
        print('POST REQUEST STARTED')
        # Get values
        has_errors = False
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        password = request.POST.get('password', None)
        viewr = request.POST.get('viewr', None)
    
        # Validate
        # 
        if not viewr:
            has_errors = True
            viewr_error = 'Subject is required.'

        try:
            # pass in request object
            hs = get_oauth_hs(request)

        # # your logic goes here. For example: list all HydroShare resources
        #     for resource in hs.getResourceList():
        #         print(resource)

        except Exception as e:
    # handle exceptions
        
            if not username:
                has_errors = True
                username_error = 'Username is required.'
            
            elif not password:
                has_errors = True
                password_error = 'Password is required.'

            else:
                auth = HydroShareAuthBasic(username= username, password= password)
                hs = HydroShare(auth=auth)

        

        if not has_errors:
            # Do stuff here

            result = hs.resources(subject=viewr)

            resourceList = []
            for resource in result:
                resourceList.append(resource)

            return HttpResponse(json.dumps(resourceList))
            # return {"status": success }
        if has_errors:    
        #Utah Municipal resource id
            messages.error(request, "Please fix errors.")

    # Define form gizmos

    username_input = TextInput(
        display_text='Username',
        name='username',
        placeholder='Enter your username'
    )

    viewr_input = TextInput(
        display_text='Subject',
        name='viewr',
        placeholder='Enter your subject'
    )

    password_input = TextInput(
        display_text='Password',
        name='password',
        attributes={"type":"password"},
        placeholder='Enter your password'
    ) 

    # river_input = TextInput(
    #     display_text='Name of Creator',
    #     name='river',
    #     placeholder='e.g: John Smith'
    # )


    add_button = Button(
        display_text='Add',
        name='add-button',
        icon='glyphicon glyphicon-plus',
        style='success',
        attributes={'form': 'add-dam-form'},
        submit=True
    )

    cancel_button = Button(
        display_text='Cancel',
        name='cancel-button',
        href=reverse('hydroshare_python:home')
    )

    context = {
        'loggedin' : loggedin,
        'username_input': username_input,
        'password_input': password_input,
        'viewr_input': viewr_input,
        'add_button': add_button,
        'cancel_button': cancel_button,
        'resourcev': resourcev
    }

    return render(request, 'hydroshare_python/find_resource.html', context)

@login_required()
def download_resource(request):
    """
    Controller for the Add Dam page.
    """
    # Default Values
    title = ''
    username = ''
    password = ''
    

    # Errors
    title_error = ''
    username_error = ''
    password_error = ''
    loggedin = False
    try:
            # pass in request object
        hs = get_oauth_hs(request)
        loggedin = True

    except Exception as e:
        pass


    # Handle form submission
    if request.POST and 'download-button' in request.POST:
        # Get values
        has_errors = False
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        title = request.POST.get('title', None)
        

        # Validate
        if not title:
            has_errors = True
            title_error = 'Title is required.'

        
        try:
            # pass in request object
            hs = get_oauth_hs(request)

        # your logic goes here. For example: list all HydroShare resources
            # for resource in hs.getResourceList():
            #     print(resource)

        except Exception as e:
    # handle exceptions
        
            if not username:
                has_errors = True
                username_error = 'Username is required.'
            
            elif not password:
                has_errors = True
                password_error = 'Password is required.'

            else:
                auth = HydroShareAuthBasic(username= username, password= password)
                hs = HydroShare(auth=auth)

        if not has_errors:
            # Do stuff here
            # auth = HydroShareAuthBasic(username= username, password= password)
            # hs = HydroShare(auth=auth)
            fpath='/tmp/%s.zip' % title
            hs.getResource(title, destination='/tmp')
            # response = HttpResponse( content_type='application/force-download')
            # response['Content-Disposition'] = 'attachment; filename=%s.zip' % smart_str(title)
            # response['X-Sendfile'] = smart_str('/tmp')
            # response['Content-Length'] = os.path.getsize(fpath)
            # print(os.path.getsize(fpath))

            wrapper = FileWrapper(open(os.path.abspath(fpath), 'rb')) 
            response = HttpResponse(wrapper, content_type='text/plain') 
            response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(fpath) 
            response['Content-Length'] = os.path.getsize(fpath)
            return response
            # hs.setAccessRules(public=True)
            
        if has_errors:    
        #Utah Municipal resource id
            messages.error(request, "Please fix errors.")

    # Define form gizmos
    title_input = TextInput(
        display_text='Enter your resource ID of the Resource',
        name='title',
        placeholder= 'Ex: decbdccf486d4df4b1d18031a4e63aa3'
    )

    username_input = TextInput(
        display_text='Username',
        name='username',
        placeholder='Enter your username'
    )

    password_input = TextInput(
        display_text='Password',
        name='password',
        attributes={"type":"password"},
        placeholder='Enter your password'
    ) 

    # river_input = TextInput(
    #     display_text='Name of Creator',
    #     name='river',
    #     placeholder='e.g: John Smith'
    # )


    download_button = Button(
        display_text='Download',
        name='download-button',
        icon='glyphicon glyphicon-plus',
        style='success',
        attributes={'form': 'add-dam-form'},
        submit=True
    )

    cancel_button = Button(
        display_text='Cancel',
        name='cancel-button',
        href=reverse('hydroshare_python:home')
    )

    context = {
        'loggedin' : loggedin,
        'title_input': title_input,
        'username_input': username_input,
        'password_input': password_input,
        'download_button': download_button,
        'cancel_button': cancel_button,
    }

    return render(request, 'hydroshare_python/download_resource.html', context)


@login_required()
def create_folder(request):
    """
    Controller for the Add Dam page.
    """
    # Default Values
    username = ''
    password = ''
    # river = ''
    resourcein = ''
    foldername = ''
    

    # Errors
    username_error = ''
    password_error = ''
    # river_error = ''
    resourcein_error = ''
    foldername_error = ''
    loggedin = False
    try:
            # pass in request object
        hs = get_oauth_hs(request)
        loggedin = True

    except Exception as e:
        pass


    # Handle form submission
    if request.POST and 'create-button' in request.POST:
        # Get values
        has_errors = False
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        # river = request.POST.get('river', None)
        resourcein = request.POST.get('resourcein', None)
        foldername = request.POST.get('foldername', None)
        

        # Validate
        if not resourcein:
            has_errors = True
            resourcein_error = 'resourcein is required.'

        try:
            # pass in request object
            hs = get_oauth_hs(request)

        # # your logic goes here. For example: list all HydroShare resources
        #     for resource in hs.getResourceList():
        #         print(resource)

        except Exception as e:
    # handle exceptions
        
            if not username:
                has_errors = True
                username_error = 'Username is required.'
            
            elif not password:
                has_errors = True
                password_error = 'Password is required.'

            else:
                auth = HydroShareAuthBasic(username= username, password= password)
                hs = HydroShare(auth=auth)
        
           
        if not foldername:
            has_errors = True
            foldername_error = 'Folder name is required.'

        if not has_errors:
            # Do stuff here
            # auth = HydroShareAuthBasic(username= username, password= password)
            # hs = HydroShare(auth=auth)
            folder_to_create = foldername
            response_json = hs.createResourceFolder(resourcein, pathname=folder_to_create)
            messages.success(request, "Folder created successfully")
        if has_errors:    
            messages.error(request, "Please fix errors.")

    # Define form gizmos
    username_input = TextInput(
        display_text='Username',
        name='username',
        placeholder='Enter your username'
    )

    password_input = TextInput(
        display_text='Password',
        name='password',
        attributes={"type":"password"},
        placeholder='Enter your password'
    ) 

    
    foldername_input = TextInput(
        display_text='Name of the Folder',
        name='foldername',
        placeholder='Enter the name of the folder'
    )
    
    resourcein_input = TextInput(
        display_text='Resource ID',
        name='resourcein',
        placeholder='Enter the Resource ID'
    )

    create_button = Button(
        display_text='Create Folder',
        name='create-button',
        icon='glyphicon glyphicon-plus',
        style='success',
        attributes={'form': 'add-dam-form'},
        submit=True
    )

    cancel_button = Button(
        display_text='Cancel',
        name='cancel-button',
        href=reverse('hydroshare_python:home')
    )

    context = {
        'loggedin' : loggedin,
        'username_input': username_input,
        'password_input': password_input,
        'resourcein_input': resourcein_input,
        'create_button': create_button,
        'cancel_button': cancel_button,
        'foldername_input': foldername_input,
    }

    return render(request, 'hydroshare_python/create_folder.html', context)


@login_required()
def deletefolder(request):
    """
    Controller for the Add Dam page.
    """
    # Default Values
    username = ''
    password = ''
    # river = ''
    resourcein = ''
    foldername = ''
    

    # Errors
    username_error = ''
    password_error = ''
    # river_error = ''
    resourcein_error = ''
    foldername_error = ''
    loggedin = False
    try:
            # pass in request object
        hs = get_oauth_hs(request)
        loggedin = True

    except Exception as e:
        pass


    # Handle form submission
    if request.POST and 'create-button' in request.POST:
        # Get values
        has_errors = False
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        # river = request.POST.get('river', None)
        resourcein = request.POST.get('resourcein', None)
        foldername = request.POST.get('foldername', None)
        

        # Validate
        if not resourcein:
            has_errors = True
            resourcein_error = 'resourcein is required.'

        try:
            # pass in request object
            hs = get_oauth_hs(request)

        # your logic goes here. For example: list all HydroShare resources
            # for resource in hs.getResourceList():
            #     print(resource)

        except Exception as e:
    # handle exceptions
        
            if not username:
                has_errors = True
                username_error = 'Username is required.'
            
            elif not password:
                has_errors = True
                password_error = 'Password is required.'

            else:
                auth = HydroShareAuthBasic(username= username, password= password)
                hs = HydroShare(auth=auth)
        
        
        if not foldername:
            has_errors = True
            foldername_error = 'Folder name is required.'

        if not has_errors:
            # Do stuff here
            # auth = HydroShareAuthBasic(username= username, password= password)
            # hs = HydroShare(auth=auth)
            folder_to_create = foldername
            response_json = hs.deleteResourceFolder(resourcein, pathname=folder_to_create)
            messages.success(request, "Folder deleted successfully")
        if has_errors:    
            messages.error(request, "Please fix errors.")

    # Define form gizmos
    username_input = TextInput(
        display_text='Username',
        name='username',
        placeholder='Enter your username'
    )

    password_input = TextInput(
        display_text='Password',
        name='password',
        attributes={"type":"password"},
        placeholder='Enter your password'
    ) 

    
    foldername_input = TextInput(
        display_text='Name of the Folder',
        name='foldername',
        placeholder='Enter the name of the folder'
    )
    
    resourcein_input = TextInput(
        display_text='Resource ID',
        name='resourcein',
        placeholder='Enter the Resource ID'
    )

    create_button = Button(
        display_text='Delete Folder',
        name='create-button',
        icon='glyphicon glyphicon-plus',
        style='success',
        attributes={'form': 'add-dam-form'},
        submit=True
    )

    cancel_button = Button(
        display_text='Cancel',
        name='cancel-button',
        href=reverse('hydroshare_python:home')
    )

    context = {
        'loggedin' : loggedin,
        'username_input': username_input,
        'password_input': password_input,
        'resourcein_input': resourcein_input,
        'create_button': create_button,
        'cancel_button': cancel_button,
        'foldername_input': foldername_input,
    }

    return render(request, 'hydroshare_python/deletefolder.html', context)



@login_required()
def change_public(request):
    """
    Controller for the Add Dam page.
    """
    # Default Values
    title = ''
    username = ''
    password = ''
    

    # Errors
    title_error = ''
    username_error = ''
    password_error = ''
    loggedin = False
    try:
            # pass in request object
        hs = get_oauth_hs(request)
        loggedin = True

    except Exception as e:
        pass

    # Handle form submission
    if request.POST and 'public-button' in request.POST:
        # Get values
        has_errors = False
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        title = request.POST.get('title', None)
        

        # Validate
        if not title:
            has_errors = True
            title_error = 'Title is required.'

        
        try:
            # pass in request object
            hs = get_oauth_hs(request)

        # your logic goes here. For example: list all HydroShare resources
            # for resource in hs.getResourceList():
            #     print(resource)

        except Exception as e:
    # handle exceptions
        
            if not username:
                has_errors = True
                username_error = 'Username is required.'
            
            elif not password:
                has_errors = True
                password_error = 'Password is required.'

            else:
                auth = HydroShareAuthBasic(username= username, password= password)
                hs = HydroShare(auth=auth)

        if not has_errors:
            # Do stuff here
            # auth = HydroShareAuthBasic(username= username, password= password)
            # hs = HydroShare(auth=auth)
            hs.setAccessRules(title, public=True)
            messages.success(request, "Resource is now public")
            # hs.setAccessRules(public=True)
            
        if has_errors:    
        #Utah Municipal resource id
            messages.error(request, "Please fix errors.")

    # Define form gizmos
    title_input = TextInput(
        display_text='Enter your resource ID of the Resource',
        name='title',
        placeholder= 'Ex: decbdccf486d4df4b1d18031a4e63aa3'
    )

    username_input = TextInput(
        display_text='Username',
        name='username',
        placeholder='Enter your username'
    )

    password_input = TextInput(
        display_text='Password',
        name='password',
        attributes={"type":"password"},
        placeholder='Enter your password'
    ) 

    # river_input = TextInput(
    #     display_text='Name of Creator',
    #     name='river',
    #     placeholder='e.g: John Smith'
    # )


    public_button = Button(
        display_text='Change to Public',
        name='public-button',
        icon='glyphicon glyphicon-plus',
        style='success',
        attributes={'form': 'add-dam-form'},
        submit=True
    )

    cancel_button = Button(
        display_text='Cancel',
        name='cancel-button',
        href=reverse('hydroshare_python:home')
    )

    context = {
        'loggedin' : loggedin,
        'title_input': title_input,
        'username_input': username_input,
        'password_input': password_input,
        'public_button': public_button,
        'cancel_button': cancel_button,
    }

    return render(request, 'hydroshare_python/change_public.html', context)