def gldas_variables():
    return {
        'Air temperature': 'Tair_f_tavg',
        'Downward heat flux in soil': 'Qg_tavg',
        'Green vegetation fraction': 'Greenness_inst',
        'Liquid water content of surface snow': 'SWE_tavg',
        'Potential evapotranspiration': 'PotEvap_tavg',
        'Precipitation rate': 'Rainf_tavg',
        'Rainfall flux': 'Rainf_f_tavg',
        'Snow depth': 'SnowDepth_inst',
        'Snowfall rate': 'Snowf_tavg',
        'Specific humidity': 'Qair_f_tavg',
        'Subsurface runoff amount': 'Qsb_tavg',
        'Surface air pressure': 'Psurf_f_tavg',
        'Surface albedo': 'Albedo_tavg',
        'Surface downwelling longwave flux in air': 'LWdown_f_tavg',
        'Surface downwelling shortwave flux in air': 'SWdown_f_tavg',
        'Surface net downward longwave flux': 'Lwnet_tavg',
        'Surface net downward shortwave flux': 'Swnet_tavg',
        'Surface runoff amount': 'Qs_tavg',
        'Surface snow area fraction': 'SnowCover_tavg',
        'Surface temperature': 'AvgSurfT_tavg',
        'Surface upward latent heat flux': 'Qle_tavg',
        'Surface upward sensible heat flux': 'Qh_tavg',
        'Total evapotranspiration': 'Evap_tavg',
        'Wind speed': 'Wind_f_tavg'
    }


def available_dates():
    """
    gets the available dates to show on the map based on the path to data Custom Setting
    """
    import os, datetime
    from .app import Malaria as App
    dates = os.listdir(App.get_custom_setting('datadirpath'))
    date_opts = []
    for i in range(len(dates)):
        if dates[i].startswith('.'):
            continue
        date = dates[i].replace('LIS_HIST_', '').replace('.nc', '')
        tmp = datetime.datetime.strptime(date, '%Y%m%d')
        date_opts.append((datetime.datetime.strftime(tmp, '%b %d %Y'), date))
        date_opts.sort()
    del dates, tmp

    return date_opts


def wms_colors():
    """
    Color options usable by thredds wms
    """
    return [
        ('SST-36', 'sst_36'),
        ('Greyscale', 'greyscale'),
        ('Rainbow', 'rainbow'),
        ('OCCAM', 'occam'),
        ('OCCAM Pastel', 'occam_pastel-30'),
        ('Red-Blue', 'redblue'),
        ('NetCDF Viewer', 'ncview'),
        ('ALG', 'alg'),
        ('ALG 2', 'alg2'),
        ('Ferret', 'ferret'),
        ]


def ubigeo_to_distname():
    return {

    }
