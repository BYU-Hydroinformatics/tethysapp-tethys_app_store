import dask
import requests
from .interpolation_utils import process_interpolation

# from .interpolation_utils import process_interpolation

INFO_DICT = {'region': '3',
             'aquifer': '24',
             'variable': '1',
             'porosity': '0.1',
             'spatial_interpolation': 'IDW',
             'temporal_interpolation': 'MLR',
             'search_radius': '0.1',
             'ndmin': '5',
             'ndmax': '15',
             'start_date': '1970',
             'end_date': '1980',
             'resolution': '0.05',
             'min_ratio': '0.25',
             'time_tolerance': '20',
             'frequency': '5',
             'default': '0',
             'min_samples': '10',
             'seasonal': '999',
             'from_wizard': 'true',
             'gap_size': '365 days',
             'pad': '90',
             'spacing': '1MS'}


def dask_interp(info_dict):
    result = process_interpolation(info_dict)
    return result


# Delayed Job
def delayed_job(info_dict):
    return dask.delayed(dask_interp(info_dict), pure=False)
