from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from tethys_sdk.gizmos import *
from .app import *
from .model import *
from .utilities import *
from .config import get_thredds_url, get_global_netcdf_dir, SHELL_DIR
from .update_global_data import *

# @login_required()


def home(request):
    """
    Controller for the app home page.
    """

    # downloadFile(get_global_netcdf_dir()+'temp4/')
    # write_gldas_text_file()
    # download_gldas_data()
    # download_monthly_gldas_data()

    Session = Newgrace.get_persistent_store_database('gracefo_db', as_sessionmaker=True)
    session = Session()
    # Query DB for regions
    regions = session.query(Region).all()
    region_list = []

    for region in regions:
        region_list.append(("%s" % (region.display_name), region.id))

    session.close()
    if region_list:
        region_select = SelectInput(display_text='Select a Region',
                                    name='region-select',
                                    options=region_list, )
    else:
        region_select = None

    context = {
        "region_select": region_select, "regions_length": len(region_list), 'host': 'http://%s' % request.get_host()
    }

    return render(request, 'newgrace/home.html', context)


def api(request):

    context = {'host': 'http://%s' % request.get_host()}

    return render(request, 'grace/api.html', context)

# @login_required()


def global_map(request):
    """
    Controller for the app home page.
    """
    thredds_wms = get_thredds_url()

    # grace_layer_options = get_global_dates()
    # print(grace_layer_options)

    select_signal_process = SelectInput(display_text='Select Signal Processing Method',
                                        name='select_signal_process',
                                        multiple=False,
                                        options=[('CSR Solution', "csr"), ('JPL Solution', "jpl"),
                                                 ('GFZ Solution', "gfz"), ('Ensemble Avg of JPL, CSR, & GFZ', "avg")],
                                        initial=['JPL Solution']
                                        )

    select_layer = SelectInput(display_text='Select a day',
                               name='select_layer',
                               multiple=False,
                               options=[['2002 April 16', '2002-04-16:00:00:00'], ['2002 May 10', '2002-05-10:00:00:00'], ['2002 August 16', '2002-08-16:12:00:00'], ['2002 September 16', '2002-09-16:00:00:00'], ['2002 October 16', '2002-10-16:12:00:00'], ['2002 November 16', '2002-11-16:00:00:00'], ['2002 December 16', '2002-12-16:12:00:00'], ['2003 January 16', '2003-01-16:12:00:00'], ['2003 February 15', '2003-02-15:00:00:00'], ['2003 March 16', '2003-03-16:12:00:00'], ['2003 April 16', '2003-04-16:00:00:00'], ['2003 May 11', '2003-05-11:12:00:00'], ['2003 July 16', '2003-07-16:12:00:00'], ['2003 August 16', '2003-08-16:12:00:00'], ['2003 September 16', '2003-09-16:00:00:00'], ['2003 October 16', '2003-10-16:12:00:00'], ['2003 November 16', '2003-11-16:00:00:00'], ['2003 December 16', '2003-12-16:12:00:00'], ['2004 January 07', '2004-01-07:12:00:00'], ['2004 February 17', '2004-02-17:00:00:00'], ['2004 March 16', '2004-03-16:12:00:00'], ['2004 April 16', '2004-04-16:00:00:00'], ['2004 May 16', '2004-05-16:12:00:00'], ['2004 June 16', '2004-06-16:00:00:00'], ['2004 July 16', '2004-07-16:12:00:00'], ['2004 August 16', '2004-08-16:12:00:00'], ['2004 September 16', '2004-09-16:00:00:00'], ['2004 October 16', '2004-10-16:12:00:00'], ['2004 November 16', '2004-11-16:00:00:00'], ['2004 December 16', '2004-12-16:12:00:00'], ['2005 January 16', '2005-01-16:12:00:00'], ['2005 February 15', '2005-02-15:00:00:00'], ['2005 March 16', '2005-03-16:12:00:00'], ['2005 April 16', '2005-04-16:00:00:00'], ['2005 May 16', '2005-05-16:12:00:00'], ['2005 June 16', '2005-06-16:00:00:00'], ['2005 July 16', '2005-07-16:12:00:00'], ['2005 August 16', '2005-08-16:12:00:00'], ['2005 September 16', '2005-09-16:00:00:00'], ['2005 October 16', '2005-10-16:12:00:00'], ['2005 November 16', '2005-11-16:00:00:00'], ['2005 December 16', '2005-12-16:12:00:00'], ['2006 January 16', '2006-01-16:12:00:00'], ['2006 February 15', '2006-02-15:00:00:00'], ['2006 March 16', '2006-03-16:12:00:00'], ['2006 April 16', '2006-04-16:00:00:00'], ['2006 May 16', '2006-05-16:12:00:00'], ['2006 June 16', '2006-06-16:00:00:00'], ['2006 July 16', '2006-07-16:12:00:00'], ['2006 August 16', '2006-08-16:12:00:00'], ['2006 September 16', '2006-09-16:00:00:00'], ['2006 October 16', '2006-10-16:12:00:00'], ['2006 November 16', '2006-11-16:00:00:00'], ['2006 December 16', '2006-12-16:12:00:00'], ['2007 January 16', '2007-01-16:12:00:00'], ['2007 February 15', '2007-02-15:00:00:00'], ['2007 March 16', '2007-03-16:12:00:00'], ['2007 April 16', '2007-04-16:00:00:00'], ['2007 May 16', '2007-05-16:12:00:00'], ['2007 June 16', '2007-06-16:00:00:00'], ['2007 July 16', '2007-07-16:12:00:00'], ['2007 August 16', '2007-08-16:12:00:00'], ['2007 September 16', '2007-09-16:00:00:00'], ['2007 October 16', '2007-10-16:12:00:00'], ['2007 November 16', '2007-11-16:00:00:00'], ['2007 December 16', '2007-12-16:12:00:00'], ['2008 January 16', '2008-01-16:12:00:00'], ['2008 February 15', '2008-02-15:12:00:00'], ['2008 March 16', '2008-03-16:12:00:00'], ['2008 April 16', '2008-04-16:00:00:00'], ['2008 May 16', '2008-05-16:12:00:00'], ['2008 June 16', '2008-06-16:00:00:00'], ['2008 July 16', '2008-07-16:12:00:00'], ['2008 August 16', '2008-08-16:12:00:00'], ['2008 September 16', '2008-09-16:00:00:00'], ['2008 October 16', '2008-10-16:12:00:00'], ['2008 November 16', '2008-11-16:00:00:00'], ['2008 December 16', '2008-12-16:12:00:00'], ['2009 January 16', '2009-01-16:12:00:00'], ['2009 February 15', '2009-02-15:00:00:00'], ['2009 March 16', '2009-03-16:12:00:00'], ['2009 April 16', '2009-04-16:00:00:00'], ['2009 May 16', '2009-05-16:12:00:00'], [
                                   '2009 June 16', '2009-06-16:00:00:00'], ['2009 July 16', '2009-07-16:12:00:00'], ['2009 August 16', '2009-08-16:12:00:00'], ['2009 September 16', '2009-09-16:00:00:00'], ['2009 October 16', '2009-10-16:12:00:00'], ['2009 November 16', '2009-11-16:00:00:00'], ['2009 December 16', '2009-12-16:12:00:00'], ['2010 January 16', '2010-01-16:12:00:00'], ['2010 February 15', '2010-02-15:00:00:00'], ['2010 March 16', '2010-03-16:12:00:00'], ['2010 April 16', '2010-04-16:00:00:00'], ['2010 May 16', '2010-05-16:12:00:00'], ['2010 June 16', '2010-06-16:00:00:00'], ['2010 July 16', '2010-07-16:12:00:00'], ['2010 August 16', '2010-08-16:12:00:00'], ['2010 September 16', '2010-09-16:00:00:00'], ['2010 October 16', '2010-10-16:12:00:00'], ['2010 November 16', '2010-11-16:00:00:00'], ['2010 December 16', '2010-12-16:12:00:00'], ['2011 February 18', '2011-02-18:12:00:00'], ['2011 March 16', '2011-03-16:12:00:00'], ['2011 April 16', '2011-04-16:00:00:00'], ['2011 May 16', '2011-05-16:12:00:00'], ['2011 July 19', '2011-07-19:12:00:00'], ['2011 August 16', '2011-08-16:12:00:00'], ['2011 September 16', '2011-09-16:00:00:00'], ['2011 October 16', '2011-10-16:12:00:00'], ['2011 November 01', '2011-11-01:12:00:00'], ['2012 January 02', '2012-01-02:00:00:00'], ['2012 January 16', '2012-01-16:12:00:00'], ['2012 February 15', '2012-02-15:12:00:00'], ['2012 March 16', '2012-03-16:12:00:00'], ['2012 April 10', '2012-04-10:12:00:00'], ['2012 June 16', '2012-06-16:00:00:00'], ['2012 July 16', '2012-07-16:12:00:00'], ['2012 August 16', '2012-08-16:12:00:00'], ['2012 September 13', '2012-09-13:00:00:00'], ['2012 November 20', '2012-11-20:00:00:00'], ['2012 December 16', '2012-12-16:12:00:00'], ['2013 January 16', '2013-01-16:12:00:00'], ['2013 February 14', '2013-02-14:00:00:00'], ['2013 April 21', '2013-04-21:12:00:00'], ['2013 May 16', '2013-05-16:12:00:00'], ['2013 June 16', '2013-06-16:00:00:00'], ['2013 July 16', '2013-07-16:12:00:00'], ['2013 October 16', '2013-10-16:12:00:00'], ['2013 November 16', '2013-11-16:00:00:00'], ['2013 December 16', '2013-12-16:12:00:00'], ['2014 January 09', '2014-01-09:12:00:00'], ['2014 March 17', '2014-03-17:12:00:00'], ['2014 April 16', '2014-04-16:00:00:00'], ['2014 May 16', '2014-05-16:12:00:00'], ['2014 June 13', '2014-06-13:00:00:00'], ['2014 August 16', '2014-08-16:12:00:00'], ['2014 September 16', '2014-09-16:00:00:00'], ['2014 October 16', '2014-10-16:12:00:00'], ['2014 November 17', '2014-11-17:00:00:00'], ['2015 January 22', '2015-01-22:12:00:00'], ['2015 February 15', '2015-02-15:00:00:00'], ['2015 March 16', '2015-03-16:12:00:00'], ['2015 April 16', '2015-04-16:00:00:00'], ['2015 April 27', '2015-04-27:00:00:00'], ['2015 July 15', '2015-07-15:12:00:00'], ['2015 August 16', '2015-08-16:12:00:00'], ['2015 September 14', '2015-09-14:12:00:00'], ['2015 December 23', '2015-12-23:00:00:00'], ['2016 January 16', '2016-01-16:12:00:00'], ['2016 February 14', '2016-02-14:00:00:00'], ['2016 March 16', '2016-03-16:12:00:00'], ['2016 May 20', '2016-05-20:12:00:00'], ['2016 June 16', '2016-06-16:00:00:00'], ['2016 July 15', '2016-07-15:12:00:00'], ['2016 August 21', '2016-08-21:12:00:00'], ['2018 June 16', '2018-06-16:00:00:00'], ['2018 July 10', '2018-07-10:00:00:00'], ['2018 October 31', '2018-10-31:12:00:00'], ['2018 November 16', '2018-11-16:00:00:00'], ['2018 December 16', '2018-12-16:12:00:00'], ['2019 January 16', '2019-01-16:12:00:00'], ['2019 February 14', '2019-02-14:00:00:00'], ['2019 March 16', '2019-03-16:12:00:00'], ['2019 April 16', '2019-04-16:00:00:00'], ['2019 May 16', '2019-05-16:12:00:00'], ['2019 June 16', '2019-06-16:00:00:00']]
                               # options=grace_layer_options,
                               )

    select_storage_type = SelectInput(display_text='Select Storage Component',
                                      name='select_storage_type',
                                      multiple=False,
                                      options=[('Total Water Storage (GRACE)', "tot"),
                                               ('Surface Water Storage (GLDAS)', "sw"),
                                               ('Soil Moisture Storage (GLDAS)', "soil"),
                                               ('Groundwater Storage (Calculated)', "gw")
                                               ],
                                      initial=['Total Water Storage (GRACE)']
                                      )

    context = {
        "thredds_wms": thredds_wms,
        "select_storage_type": select_storage_type,
        'select_layer': select_layer,
        "select_signal_process": select_signal_process,

    }

    return render(request, 'newgrace/global_map.html', context)

# @login_required()


def region(request):
    """
    Controller for the app home page.
    """
    thredds_wms = get_thredds_url()

    context = {}

    info = request.GET

    region_id = info.get('region-select')
    Session = Newgrace.get_persistent_store_database('gracefo_db', as_sessionmaker=True)
    session = Session()

    region = session.query(Region).get(region_id)
    display_name = region.display_name
    region_area = region.reg_area

    bbox = [float(x) for x in region.latlon_bbox.strip("(").strip(")").split(',')]
    json.dumps(bbox)

    regions = session.query(Region).all()
    region_list = []

    for reg in regions:
        region_list.append(("%s" % (reg.display_name), reg.id))
    lower_name = ''.join(display_name.split()).lower()
    session.close()
    if region_list:
        select_region = SelectInput(display_text='Switch Region:',
                                    name='region-select',
                                    multiple=False,
                                    options=region_list,
                                    initial=display_name,
                                    )
    else:
        select_region = None

    # grace_layer_options = get_global_dates()

    # print(grace_layer_options)

    select_signal_process = SelectInput(display_text='Select Signal Processing Method',
                                        name='select_signal_process',
                                        multiple=False,
                                        options=[('JPL Solution', "jpl"), ('CSR Solution', "csr"),
                                                 ('GFZ Solution', "gfz"), ('Ensemble Avg of JPL, CSR, & GFZ', "avg")],
                                        initial=['CSR Solution']
                                        )

    select_layer = SelectInput(display_text='Select a day',
                               name='select_layer',
                               multiple=False,
                               options=[['2002 April 16', '2002-04-16:00:00:00'], ['2002 May 10', '2002-05-10:00:00:00'], ['2002 August 16', '2002-08-16:12:00:00'], ['2002 September 16', '2002-09-16:00:00:00'], ['2002 October 16', '2002-10-16:12:00:00'], ['2002 November 16', '2002-11-16:00:00:00'], ['2002 December 16', '2002-12-16:12:00:00'], ['2003 January 16', '2003-01-16:12:00:00'], ['2003 February 15', '2003-02-15:00:00:00'], ['2003 March 16', '2003-03-16:12:00:00'], ['2003 April 16', '2003-04-16:00:00:00'], ['2003 May 11', '2003-05-11:12:00:00'], ['2003 July 16', '2003-07-16:12:00:00'], ['2003 August 16', '2003-08-16:12:00:00'], ['2003 September 16', '2003-09-16:00:00:00'], ['2003 October 16', '2003-10-16:12:00:00'], ['2003 November 16', '2003-11-16:00:00:00'], ['2003 December 16', '2003-12-16:12:00:00'], ['2004 January 07', '2004-01-07:12:00:00'], ['2004 February 17', '2004-02-17:00:00:00'], ['2004 March 16', '2004-03-16:12:00:00'], ['2004 April 16', '2004-04-16:00:00:00'], ['2004 May 16', '2004-05-16:12:00:00'], ['2004 June 16', '2004-06-16:00:00:00'], ['2004 July 16', '2004-07-16:12:00:00'], ['2004 August 16', '2004-08-16:12:00:00'], ['2004 September 16', '2004-09-16:00:00:00'], ['2004 October 16', '2004-10-16:12:00:00'], ['2004 November 16', '2004-11-16:00:00:00'], ['2004 December 16', '2004-12-16:12:00:00'], ['2005 January 16', '2005-01-16:12:00:00'], ['2005 February 15', '2005-02-15:00:00:00'], ['2005 March 16', '2005-03-16:12:00:00'], ['2005 April 16', '2005-04-16:00:00:00'], ['2005 May 16', '2005-05-16:12:00:00'], ['2005 June 16', '2005-06-16:00:00:00'], ['2005 July 16', '2005-07-16:12:00:00'], ['2005 August 16', '2005-08-16:12:00:00'], ['2005 September 16', '2005-09-16:00:00:00'], ['2005 October 16', '2005-10-16:12:00:00'], ['2005 November 16', '2005-11-16:00:00:00'], ['2005 December 16', '2005-12-16:12:00:00'], ['2006 January 16', '2006-01-16:12:00:00'], ['2006 February 15', '2006-02-15:00:00:00'], ['2006 March 16', '2006-03-16:12:00:00'], ['2006 April 16', '2006-04-16:00:00:00'], ['2006 May 16', '2006-05-16:12:00:00'], ['2006 June 16', '2006-06-16:00:00:00'], ['2006 July 16', '2006-07-16:12:00:00'], ['2006 August 16', '2006-08-16:12:00:00'], ['2006 September 16', '2006-09-16:00:00:00'], ['2006 October 16', '2006-10-16:12:00:00'], ['2006 November 16', '2006-11-16:00:00:00'], ['2006 December 16', '2006-12-16:12:00:00'], ['2007 January 16', '2007-01-16:12:00:00'], ['2007 February 15', '2007-02-15:00:00:00'], ['2007 March 16', '2007-03-16:12:00:00'], ['2007 April 16', '2007-04-16:00:00:00'], ['2007 May 16', '2007-05-16:12:00:00'], ['2007 June 16', '2007-06-16:00:00:00'], ['2007 July 16', '2007-07-16:12:00:00'], ['2007 August 16', '2007-08-16:12:00:00'], ['2007 September 16', '2007-09-16:00:00:00'], ['2007 October 16', '2007-10-16:12:00:00'], ['2007 November 16', '2007-11-16:00:00:00'], ['2007 December 16', '2007-12-16:12:00:00'], ['2008 January 16', '2008-01-16:12:00:00'], ['2008 February 15', '2008-02-15:12:00:00'], ['2008 March 16', '2008-03-16:12:00:00'], ['2008 April 16', '2008-04-16:00:00:00'], ['2008 May 16', '2008-05-16:12:00:00'], ['2008 June 16', '2008-06-16:00:00:00'], ['2008 July 16', '2008-07-16:12:00:00'], ['2008 August 16', '2008-08-16:12:00:00'], ['2008 September 16', '2008-09-16:00:00:00'], ['2008 October 16', '2008-10-16:12:00:00'], ['2008 November 16', '2008-11-16:00:00:00'], ['2008 December 16', '2008-12-16:12:00:00'], ['2009 January 16', '2009-01-16:12:00:00'], ['2009 February 15', '2009-02-15:00:00:00'], ['2009 March 16', '2009-03-16:12:00:00'], ['2009 April 16', '2009-04-16:00:00:00'], ['2009 May 16', '2009-05-16:12:00:00'], [
                                   '2009 June 16', '2009-06-16:00:00:00'], ['2009 July 16', '2009-07-16:12:00:00'], ['2009 August 16', '2009-08-16:12:00:00'], ['2009 September 16', '2009-09-16:00:00:00'], ['2009 October 16', '2009-10-16:12:00:00'], ['2009 November 16', '2009-11-16:00:00:00'], ['2009 December 16', '2009-12-16:12:00:00'], ['2010 January 16', '2010-01-16:12:00:00'], ['2010 February 15', '2010-02-15:00:00:00'], ['2010 March 16', '2010-03-16:12:00:00'], ['2010 April 16', '2010-04-16:00:00:00'], ['2010 May 16', '2010-05-16:12:00:00'], ['2010 June 16', '2010-06-16:00:00:00'], ['2010 July 16', '2010-07-16:12:00:00'], ['2010 August 16', '2010-08-16:12:00:00'], ['2010 September 16', '2010-09-16:00:00:00'], ['2010 October 16', '2010-10-16:12:00:00'], ['2010 November 16', '2010-11-16:00:00:00'], ['2010 December 16', '2010-12-16:12:00:00'], ['2011 February 18', '2011-02-18:12:00:00'], ['2011 March 16', '2011-03-16:12:00:00'], ['2011 April 16', '2011-04-16:00:00:00'], ['2011 May 16', '2011-05-16:12:00:00'], ['2011 July 19', '2011-07-19:12:00:00'], ['2011 August 16', '2011-08-16:12:00:00'], ['2011 September 16', '2011-09-16:00:00:00'], ['2011 October 16', '2011-10-16:12:00:00'], ['2011 November 01', '2011-11-01:12:00:00'], ['2012 January 02', '2012-01-02:00:00:00'], ['2012 January 16', '2012-01-16:12:00:00'], ['2012 February 15', '2012-02-15:12:00:00'], ['2012 March 16', '2012-03-16:12:00:00'], ['2012 April 10', '2012-04-10:12:00:00'], ['2012 June 16', '2012-06-16:00:00:00'], ['2012 July 16', '2012-07-16:12:00:00'], ['2012 August 16', '2012-08-16:12:00:00'], ['2012 September 13', '2012-09-13:00:00:00'], ['2012 November 20', '2012-11-20:00:00:00'], ['2012 December 16', '2012-12-16:12:00:00'], ['2013 January 16', '2013-01-16:12:00:00'], ['2013 February 14', '2013-02-14:00:00:00'], ['2013 April 21', '2013-04-21:12:00:00'], ['2013 May 16', '2013-05-16:12:00:00'], ['2013 June 16', '2013-06-16:00:00:00'], ['2013 July 16', '2013-07-16:12:00:00'], ['2013 October 16', '2013-10-16:12:00:00'], ['2013 November 16', '2013-11-16:00:00:00'], ['2013 December 16', '2013-12-16:12:00:00'], ['2014 January 09', '2014-01-09:12:00:00'], ['2014 March 17', '2014-03-17:12:00:00'], ['2014 April 16', '2014-04-16:00:00:00'], ['2014 May 16', '2014-05-16:12:00:00'], ['2014 June 13', '2014-06-13:00:00:00'], ['2014 August 16', '2014-08-16:12:00:00'], ['2014 September 16', '2014-09-16:00:00:00'], ['2014 October 16', '2014-10-16:12:00:00'], ['2014 November 17', '2014-11-17:00:00:00'], ['2015 January 22', '2015-01-22:12:00:00'], ['2015 February 15', '2015-02-15:00:00:00'], ['2015 March 16', '2015-03-16:12:00:00'], ['2015 April 16', '2015-04-16:00:00:00'], ['2015 April 27', '2015-04-27:00:00:00'], ['2015 July 15', '2015-07-15:12:00:00'], ['2015 August 16', '2015-08-16:12:00:00'], ['2015 September 14', '2015-09-14:12:00:00'], ['2015 December 23', '2015-12-23:00:00:00'], ['2016 January 16', '2016-01-16:12:00:00'], ['2016 February 14', '2016-02-14:00:00:00'], ['2016 March 16', '2016-03-16:12:00:00'], ['2016 May 20', '2016-05-20:12:00:00'], ['2016 June 16', '2016-06-16:00:00:00'], ['2016 July 15', '2016-07-15:12:00:00'], ['2016 August 21', '2016-08-21:12:00:00'], ['2018 June 16', '2018-06-16:00:00:00'], ['2018 July 10', '2018-07-10:00:00:00'], ['2018 October 31', '2018-10-31:12:00:00'], ['2018 November 16', '2018-11-16:00:00:00'], ['2018 December 16', '2018-12-16:12:00:00'], ['2019 January 16', '2019-01-16:12:00:00'], ['2019 February 14', '2019-02-14:00:00:00'], ['2019 March 16', '2019-03-16:12:00:00'], ['2019 April 16', '2019-04-16:00:00:00'], ['2019 May 16', '2019-05-16:12:00:00'], ['2019 June 16', '2019-06-16:00:00:00']]
                               # options=grace_layer_options,
                               )

    select_storage_type = SelectInput(display_text='Select Storage Component',
                                      name='select_storage_type',
                                      multiple=False,
                                      options=[('Total Water Storage (GRACE)', "tot"),
                                               ('Surface Water Storage (GLDAS)', "sw"),
                                               ('Soil Moisture Storage (GLDAS)', "soil"),
                                               ('Groundwater Storage (Calculated)', "gw")],
                                      initial=['Total Water Storage (GRACE)']
                                      )

    if bbox[0] < 0 and bbox[2] < 0:
        map_center = [(int(bbox[1])+int(bbox[3])) / 2, ((360+(int(bbox[0])))+(360+(int(bbox[2])))) / 2]
    else:
        map_center = [(int(bbox[1]) + int(bbox[3])) / 2, (int(bbox[0]) + int(bbox[2])) / 2]
    json.dumps(map_center)
    context = {"region_id": region_id,
               "regions_length": len(region_list),
               "thredds_wms": thredds_wms,
               "region_area": region_area,
               "display_name": display_name,
               "select_layer": select_layer,
               "bbox": bbox,
               "map_center": map_center,
               "select_signal_process": select_signal_process,
               "select_storage_type": select_storage_type,
               "select_region": select_region,
               "lower_name": lower_name
               }

    return render(request, 'newgrace/region.html', context)


@user_passes_test(user_permission_test)
def add_region(request):

    region_name_input = TextInput(display_text='Region Display Name',
                                  name='region-name-input',
                                  placeholder='e.g.: Utah',
                                  icon_append='glyphicon glyphicon-home',
                                  )  # Input for the Region Display Name

    Session = Newgrace.get_persistent_store_database('gracefo_db', as_sessionmaker=True)
    session = Session()
    # Query DB for geoservers
    thredds_servers = session.query(Thredds).all()
    thredds_list = []
    for thredds in thredds_servers:
        thredds_list.append(("%s (%s)" % (thredds.name, thredds.url),
                             thredds.id))

    session.close()
    if thredds_list:
        thredds_select = SelectInput(display_text='Select a Thredds server',
                                     name='thredds-select',
                                     options=thredds_list)
    else:
        thredds_select = None

    add_button = Button(display_text='Add Region',
                        icon='glyphicon glyphicon-plus',
                        style='success',
                        name='submit-add-region',
                        attributes={'id': 'submit-add-region'}, )  # Add region button

    context = {"region_name_input": region_name_input, "thredds_select": thredds_select, "add_button": add_button}

    return render(request, 'newgrace/add_region.html', context)


@user_passes_test(user_permission_test)
def add_thredds_server(request):
    """
        Controller for the app add_geoserver page.
    """

    thredds_name_input = TextInput(display_text='Thredds Server Name',
                                   name='thredds-name-input',
                                   placeholder='e.g.: BYU Thredds Server',
                                   icon_append='glyphicon glyphicon-tag', )

    thredds_url_input = TextInput(display_text='Thredds Server REST Url',
                                  name='thredds-url-input',
                                  placeholder='e.g.: http://localhost:9090/thredds/',
                                  icon_append='glyphicon glyphicon-cloud-download')

    thredds_username_input = TextInput(display_text='Thredds Server Username',
                                       name='thredds-username-input',
                                       placeholder='e.g.: admin',
                                       icon_append='glyphicon glyphicon-user', )

    add_button = Button(display_text='Add Thredds Server',
                        icon='glyphicon glyphicon-plus',
                        style='success',
                        name='submit-add-thredds-server',
                        attributes={'id': 'submit-add-thredds-server'}, )

    context = {
        'thredds_name_input': thredds_name_input,
        'thredds_url_input': thredds_url_input,
        'thredds_username_input': thredds_username_input,
        'add_button': add_button,
    }

    return render(request, 'newgrace/add_thredds_server.html', context)


@user_passes_test(user_permission_test)
def manage_regions(request):
    """
    Controller for the app manage_geoservers page.
    """
    # initialize session
    Session = Newgrace.get_persistent_store_database('gracefo_db', as_sessionmaker=True)
    session = Session()
    num_regions = session.query(Region).count()

    session.close()

    context = {
        'initial_page': 0,
        'num_regions': num_regions,
    }

    return render(request, 'newgrace/manage_regions.html', context)


@user_passes_test(user_permission_test)
def manage_regions_table(request):
    """
    Controller for the app manage_geoservers page.
    """
    # initialize session
    Session = Newgrace.get_persistent_store_database('gracefo_db', as_sessionmaker=True)
    session = Session()
    RESULTS_PER_PAGE = 5
    page = int(request.GET.get('page'))

    # Query DB for data store types
    regions = session.query(Region)\
        .order_by(Region.display_name) \
        .all()[(page * RESULTS_PER_PAGE):((page + 1)*RESULTS_PER_PAGE)]

    prev_button = Button(display_text='Previous',
                         name='prev_button',
                         attributes={'class': 'nav_button'},)

    next_button = Button(display_text='Next',
                         name='next_button',
                         attributes={'class': 'nav_button'},)

    context = {
        'prev_button': prev_button,
        'next_button': next_button,
        'regions': regions,
    }

    session.close()

    return render(request, 'newgrace/manage_regions_table.html', context)


@user_passes_test(user_permission_test)
def manage_thredds_servers(request):
    """
    Controller for the app manage_geoservers page.
    """
    # initialize session
    Session = Newgrace.get_persistent_store_database('gracefo_db', as_sessionmaker=True)
    session = Session()
    num_thredds_servers = session.query(Thredds).count()
    session.close()

    context = {
        'initial_page': 0,
        'num_thredds_servers': num_thredds_servers,
    }

    return render(request, 'newgrace/manage_thredds_servers.html', context)


@user_passes_test(user_permission_test)
def manage_thredds_servers_table(request):
    """
    Controller for the app manage_geoservers page.
    """
    # initialize session
    Session = Newgrace.get_persistent_store_database('gracefo_db', as_sessionmaker=True)
    session = Session()
    RESULTS_PER_PAGE = 5
    page = int(request.GET.get('page'))

    # Query DB for data store types
    thredds_servers = session.query(Thredds)\
        .order_by(Thredds.name, Thredds.url) \
        .all()[(page * RESULTS_PER_PAGE):((page + 1)*RESULTS_PER_PAGE)]

    prev_button = Button(display_text='Previous',
                         name='prev_button',
                         attributes={'class': 'nav_button'},)

    next_button = Button(display_text='Next',
                         name='next_button',
                         attributes={'class': 'nav_button'},)

    context = {
        'prev_button': prev_button,
        'next_button': next_button,
        'thredds_servers': thredds_servers,
    }

    session.close()

    return render(request, 'newgrace/manage_thredds_servers_table.html', context)


def update_global_files(request):
    """
    Controller for the app update_global_files page.
    """

    update_files_button = Button(display_text='Update Files',
                                 icon='glyphicon glyphicon-cloud-download',
                                 style='success',
                                 name='submit-update-files',
                                 attributes={'onclick': 'checkForUpdates()'},
                                 )

    context = {
        'update_files_button': update_files_button,
    }

    return render(request, 'newgrace/update_global_files.html', context)
