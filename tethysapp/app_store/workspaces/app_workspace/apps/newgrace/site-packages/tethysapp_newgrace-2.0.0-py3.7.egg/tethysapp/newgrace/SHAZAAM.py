import sys
import os.path
import subprocess
from area import area
import fiona
import shapely.geometry
import rtree
import tempfile, shutil
from .app import Newgrace
from .config import *
from django.http import JsonResponse, HttpResponse, Http404
from .model import *


def subset2(shapefile,region_name,GLOBAL_DIR,display_name,thredds_id):

        SHP_DIR = SHAPE_DIR


        SHP_DIR = os.path.join(SHP_DIR, '')

        temp_dir = tempfile.mkdtemp()
        for f in shapefile:
            f_name = f.name
            f_path = os.path.join(SHP_DIR, f_name)

            with open(f_path, 'wb') as f_local:
                f_local.write(f.read())

        for file in os.listdir(SHP_DIR):
            # Reading the shapefile only
            if file.endswith(".shp"):
                f_path = os.path.join(SHP_DIR, file)
                pol_shp = f_path
                pol_name = os.path.splitext(f_name)[0]




        # Convert Polygon to netcdf file format and subset netcdf files to region
        # os.system(SHELL_DIR+'grace2subset.sh '+region_name+' '+GLOBAL_DIR+' '+pol_name+' '+pol_shp)

        # os.system(SHELL_DIR+'subset_initial.sh '+region_name+' '+GLOBAL_DIR+' '+pol_name+' '+pol_shp)
        # print('Subsetting Region Bounds')
        # os.system(SHELL_DIR+'subset_jpl_tot.sh '+region_name+' '+GLOBAL_DIR+' '+pol_name+' '+pol_shp)
        # print('Subsetting JPL Total Storage')
        # os.system(SHELL_DIR+'subset_jpl_gw.sh '+region_name+' '+GLOBAL_DIR+' '+pol_name+' '+pol_shp)
        # print('Subsetting JPL Groundwater Storage')
        # os.system(SHELL_DIR+'subset_csr_tot.sh '+region_name+' '+GLOBAL_DIR+' '+pol_name+' '+pol_shp)
        # print('Subsetting CSR Total Storage')
        # os.system(SHELL_DIR+'subset_csr_gw.sh '+region_name+' '+GLOBAL_DIR+' '+pol_name+' '+pol_shp)
        # print('Subsetting CSR Groundwater Storage')
        # os.system(SHELL_DIR+'subset_gfz_tot.sh '+region_name+' '+GLOBAL_DIR+' '+pol_name+' '+pol_shp)
        # print('Subsetting GFZ Total Storage')
        # os.system(SHELL_DIR+'subset_gfz_gw.sh '+region_name+' '+GLOBAL_DIR+' '+pol_name+' '+pol_shp)
        # print('Subsetting GFZ Groundwater Storage')
        # os.system(SHELL_DIR+'subset_avg_tot.sh '+region_name+' '+GLOBAL_DIR+' '+pol_name+' '+pol_shp)
        # print('Subsetting AVG Total Storage')
        # os.system(SHELL_DIR+'subset_avg_gw.sh '+region_name+' '+GLOBAL_DIR+' '+pol_name+' '+pol_shp)
        # print('Subsetting AVG Groundwater Storage')
        # os.system(SHELL_DIR+'subset_sw.sh '+region_name+' '+GLOBAL_DIR+' '+pol_name+' '+pol_shp)
        # print('Subsetting Surface Water Storage')
        # os.system(SHELL_DIR+'subset_soil.sh '+region_name+' '+GLOBAL_DIR+' '+pol_name+' '+pol_shp)
        # print('Subsetting Soil Moisture Storage')
        # os.system(SHELL_DIR+'file_cleanup.sh '+region_name+' '+GLOBAL_DIR+' '+pol_name+' '+pol_shp)
        # print('Copying and moving files')


        # *******************************************************************************
        # Read polygon shapefile
        # *******************************************************************************

        print('Read polygon shapefile')
        gbyos_pol_lay = fiona.open(pol_shp, 'r')
        IS_pol_tot = len(gbyos_pol_lay)
        print((' - The number of polygon features is: ' + str(IS_pol_tot)))

        # *******************************************************************************
        # Create spatial index for the bounds of each polygon feature
        # *******************************************************************************
        index = rtree.index.Index()
        shp_bounds = []

        def explode(coords):
            """Explode a GeoJSON geometry's coordinates object and yield coordinate tuples.
            As long as the input is conforming, the type of the geometry doesn't matter."""
            for e in coords:
                if isinstance(e, (float, int)):
                    yield coords
                    break
                else:
                    for f in explode(e):
                        yield f

        def bbox(f):
            x, y = list(zip(*list(explode(f['geometry']['coordinates']))))
            return min(x), min(y), max(x), max(y)

        for gbyos_pol_fea in gbyos_pol_lay:
            gbyos_pol_fid = int(gbyos_pol_fea['id'])
            # the first argument of index.insert has to be 'int', not 'long' or 'str'
            gbyos_pol_shy = shapely.geometry.shape(gbyos_pol_fea['geometry'])
            index.insert(gbyos_pol_fid, gbyos_pol_shy.bounds)
            shp_bounds.append(gbyos_pol_shy.bounds)
            bbox_val = bbox(gbyos_pol_fea)
            # creates an index between the feature ID and the bounds of that feature

        # *******************************************************************************
        # Add Region to Persistent Store DB
        # *******************************************************************************


        # Session = Newgrace.get_persistent_store_database('gracefo_db', as_sessionmaker=True)
        # session = Session()
        # region = Region(thredds_id=thredds_id,display_name=display_name, latlon_bbox=str(bbox_val))
        # session.add(region)
        # session.commit()
        # session.close()
        #
        # for the_file in os.listdir(SHP_DIR):
        #     file_path = os.path.join(SHP_DIR, the_file)
        #     try:
        #         if os.path.isfile(file_path):
        #             os.unlink(file_path)
        #         #elif os.path.isdir(file_path): shutil.rmtree(file_path)
        #     except Exception as e:
        #         print(e)

        return JsonResponse({"success": "success"})


###############################################

def sub_initial(shapefile,region_name,GLOBAL_DIR,display_name,thredds_id):

        SHP_DIR = SHAPE_DIR


        SHP_DIR = os.path.join(SHP_DIR, '')

        temp_dir = tempfile.mkdtemp()
        for f in shapefile:
            f_name = f.name
            f_path = os.path.join(SHP_DIR, f_name)

            with open(f_path, 'wb') as f_local:
                f_local.write(f.read())

        for file in os.listdir(SHP_DIR):
            # Reading the shapefile only
            if file.endswith(".shp"):
                f_path = os.path.join(SHP_DIR, file)
                pol_shp = f_path
                pol_name = os.path.splitext(f_name)[0]




        os.system(SHELL_DIR+'subset_initial.sh '+region_name+' '+GLOBAL_DIR+' '+pol_name+' '+pol_shp)
        # subprocess.call('cd', shell = True)
        # os.path.join(GLOBAL_DIR, '')
        # subprocess.call('gdal_rasterize -burn 1 -l '+pol_name+' -of netcdf -te -180 -60 180 90 -co "FORMAT=NC4" -tr 0.25 0.25 '+pol_shp+' '+region_name+'.nc', shell = True)
        # subprocess.call('ncatted -a _FillValue,Band1,o,d,-99999.0 '+region_name+'.nc', shell = True)
        # subprocess.call('ncrename -O -v Band1,lwe_thickness '+region_name+'.nc', shell = True)
        # subprocess.call('ncks -O -v lwe_thickness --msa -d lon,0.0,180.0 -d lon,-180.0,-0.125 '+region_name+'.nc '+region_name+'.nc', shell = True)
        # subprocess.call('ncap2 -O -s "where(lon<0) lon=lon+360" '+region_name+'.nc '+region_name+'.nc', shell = True)

        print('Subsetting Region Bounds')

        return JsonResponse({"initial": "initial"})


def sub_jpl_tot(shapefile,region_name,GLOBAL_DIR,display_name,thredds_id):

        SHP_DIR = SHAPE_DIR

        SHP_DIR = os.path.join(SHP_DIR, '')

        for f in shapefile:
            f_name = f.name
            f_path = os.path.join(SHP_DIR, f_name)

            with open(f_path, 'wb') as f_local:
                f_local.write(f.read())

        for file in os.listdir(SHP_DIR):
            # Reading the shapefile only
            if file.endswith(".shp"):
                f_path = os.path.join(SHP_DIR, file)
                pol_shp = f_path
                pol_name = os.path.splitext(f_name)[0]


        os.system(SHELL_DIR+'subset_jpl_tot.sh '+region_name+' '+GLOBAL_DIR+' '+pol_name+' '+pol_shp)

        # os.path.join(GLOBAL_DIR, '')
        # print(GLOBAL_DIR)
        # subprocess.call('ncbo -O -y multiply GRC_jpl_tot.nc '+region_name+'.nc '+region_name+'_tot.nc', shell = True)
        # subprocess.call('ncks -A -v time GRC_jpl_tot.nc '+region_name+'_tot.nc', shell = True)
        # subprocess.call('ncwa -C -v lwe_thickness,lat,lon,time -a time '+region_name+'_tot.nc AvgTot.nc', shell = True)
        # subprocess.call('ncwa -O -v lwe_thickness -a lat,lon '+region_name+'_tot.nc teststp.nc', shell = True)
        # subprocess.call('ncap2 -A -s "where(lwe_thickness>-99998)lwe_thickness=1" '+region_name+'_tot.nc tmptot.nc', shell = True)
        # subprocess.call('ncbo -O -y mlt tmptot.nc AvgTot.nc AvgTot.nc', shell = True)
        # subprocess.call('ncdiff -O teststp.nc AvgTot.nc '+region_name+'_jpl_tot.nc', shell = True)
        # subprocess.call('ncwa -O -v lwe_thickness -a lat,lon '+region_name+'_jpl_tot.nc '+region_name+'_jpl_tot_ts.nc', shell = True)
        # subprocess.call('rm tmptot.nc', shell = True)
        # subprocess.call('rm teststp.nc', shell = True)
        # subprocess.call('rm AvgTot.nc', shell = True)
        # subprocess.call('rm '+region_name+'_tot.nc', shell = True)

        print('Subsetting JPL Total Storage')


        return JsonResponse({"jpl_tot": "jpl_tot"})


def sub_jpl_gw(shapefile,region_name,GLOBAL_DIR,display_name,thredds_id):

        SHP_DIR = SHAPE_DIR


        SHP_DIR = os.path.join(SHP_DIR, '')

        temp_dir = tempfile.mkdtemp()
        for f in shapefile:
            f_name = f.name
            f_path = os.path.join(SHP_DIR, f_name)

            with open(f_path, 'wb') as f_local:
                f_local.write(f.read())

        for file in os.listdir(SHP_DIR):
            # Reading the shapefile only
            if file.endswith(".shp"):
                f_path = os.path.join(SHP_DIR, file)
                pol_shp = f_path
                pol_name = os.path.splitext(f_name)[0]


        os.system(SHELL_DIR+'subset_jpl_gw.sh '+region_name+' '+GLOBAL_DIR+' '+pol_name+' '+pol_shp)

        # os.system('cd ' + GLOBAL_DIR)
        # os.system('ncbo -O -y multiply GRC_jpl_gw.nc ' + region_name + '.nc ' + region_name + '_gw.nc')
        # os.system('ncks -A -v time GRC_jpl_gw.nc ' + region_name + '_gw.nc')
        # os.system('ncwa -C -v lwe_thickness,lat,lon,time -a time ' + region_name + '_gw.nc AvgGW.nc')
        # os.system('ncwa -O -v lwe_thickness -a lat,lon ' + region_name + '_gw.nc teststp.nc')
        # os.system('ncap2 -A -s "where(lwe_thickness>-99998)lwe_thickness=1" ' + region_name + '_gw.nc tmpgw.nc')
        # os.system('ncbo -O -y mlt tmpgw.nc AvgGW.nc AvgGW.nc')
        # os.system('ncdiff -O teststp.nc AvgGW.nc ' + region_name + '_jpl_gw.nc')
        # os.system('ncwa -O -v lwe_thickness -a lat,lon ' + region_name + '_jpl_gw.nc ' + region_name + '_jpl_gw_ts.nc')
        # os.system('rm tmpgw.nc')
        # os.system('rm teststp.nc')
        # os.system('rm AvgGW.nc')
        # os.system('rm ' + region_name + '_gw.nc')

        print('Subsetting JPL Groundwater Storage')

        return JsonResponse({"jpl_gw": "jpl_gw"})


def sub_csr_tot(shapefile,region_name,GLOBAL_DIR,display_name,thredds_id):

        SHP_DIR = SHAPE_DIR


        SHP_DIR = os.path.join(SHP_DIR, '')

        temp_dir = tempfile.mkdtemp()
        for f in shapefile:
            f_name = f.name
            f_path = os.path.join(SHP_DIR, f_name)

            with open(f_path, 'wb') as f_local:
                f_local.write(f.read())

        for file in os.listdir(SHP_DIR):
            # Reading the shapefile only
            if file.endswith(".shp"):
                f_path = os.path.join(SHP_DIR, file)
                pol_shp = f_path
                pol_name = os.path.splitext(f_name)[0]


        os.system(SHELL_DIR+'subset_csr_tot.sh '+region_name+' '+GLOBAL_DIR+' '+pol_name+' '+pol_shp)

        # os.system('ncbo -O -y multiply GRC_csr_tot.nc ' + region_name + '.nc ' + region_name + '_tot.nc')
        # os.system('ncks -A -v time GRC_csr_tot.nc ' + region_name + '_tot.nc')
        # os.system('ncwa -C -v lwe_thickness,lat,lon,time -a time ' + region_name + '_tot.nc AvgTot.nc')
        # os.system('ncwa -O -v lwe_thickness -a lat,lon ' + region_name + '_tot.nc teststp.nc')
        # os.system('ncap2 -A -s "where(lwe_thickness>-99998)lwe_thickness=1" ' + region_name + '_tot.nc tmptot.nc')
        # os.system('ncbo -O -y mlt tmptot.nc AvgTot.nc AvgTot.nc')
        # os.system('ncdiff -O teststp.nc AvgTot.nc ' + region_name + '_csr_tot.nc')
        # os.system('ncwa -O -v lwe_thickness -a lat,lon ' + region_name + '_csr_tot.nc ' + region_name + '_csr_tot_ts.nc')
        # os.system('rm tmptot.nc')
        # os.system('rm teststp.nc')
        # os.system('rm AvgTot.nc')
        # os.system('rm ' + region_name + '_tot.nc')

        print('Subsetting CSR Total Water Storage')

        return JsonResponse({"csr_tot": "csr_tot"})


def sub_csr_gw(shapefile,region_name,GLOBAL_DIR,display_name,thredds_id):

        SHP_DIR = SHAPE_DIR


        SHP_DIR = os.path.join(SHP_DIR, '')

        temp_dir = tempfile.mkdtemp()
        for f in shapefile:
            f_name = f.name
            f_path = os.path.join(SHP_DIR, f_name)

            with open(f_path, 'wb') as f_local:
                f_local.write(f.read())

        for file in os.listdir(SHP_DIR):
            # Reading the shapefile only
            if file.endswith(".shp"):
                f_path = os.path.join(SHP_DIR, file)
                pol_shp = f_path
                pol_name = os.path.splitext(f_name)[0]


        os.system(SHELL_DIR+'subset_csr_gw.sh '+region_name+' '+GLOBAL_DIR+' '+pol_name+' '+pol_shp)

        # os.system('cd ' + GLOBAL_DIR)
        # os.system('ncbo -O -y multiply GRC_csr_gw.nc ' + region_name + '.nc ' + region_name + '_gw.nc')
        # os.system('ncks -A -v time GRC_csr_gw.nc ' + region_name + '_gw.nc')
        # os.system('ncwa -C -v lwe_thickness,lat,lon,time -a time ' + region_name + '_gw.nc AvgGW.nc')
        # os.system('ncwa -O -v lwe_thickness -a lat,lon ' + region_name + '_gw.nc teststp.nc')
        # os.system('ncap2 -A -s "where(lwe_thickness>-99998)lwe_thickness=1" ' + region_name + '_gw.nc tmpgw.nc')
        # os.system('ncbo -O -y mlt tmpgw.nc AvgGW.nc AvgGW.nc')
        # os.system('ncdiff -O teststp.nc AvgGW.nc ' + region_name + '_csr_gw.nc')
        # os.system('ncwa -O -v lwe_thickness -a lat,lon ' + region_name + '_csr_gw.nc ' + region_name + '_csr_gw_ts.nc')
        # os.system('rm tmpgw.nc')
        # os.system('rm teststp.nc')
        # os.system('rm AvgGW.nc')
        # os.system('rm ' + region_name + '_gw.nc')

        print('Subsetting CSR Groundwater Storage')

        return JsonResponse({"csr_gw": "csr_gw"})


def sub_gfz_tot(shapefile,region_name,GLOBAL_DIR,display_name,thredds_id):

        SHP_DIR = SHAPE_DIR


        SHP_DIR = os.path.join(SHP_DIR, '')

        temp_dir = tempfile.mkdtemp()
        for f in shapefile:
            f_name = f.name
            f_path = os.path.join(SHP_DIR, f_name)

            with open(f_path, 'wb') as f_local:
                f_local.write(f.read())

        for file in os.listdir(SHP_DIR):
            # Reading the shapefile only
            if file.endswith(".shp"):
                f_path = os.path.join(SHP_DIR, file)
                pol_shp = f_path
                pol_name = os.path.splitext(f_name)[0]


        os.system(SHELL_DIR+'subset_gfz_tot.sh '+region_name+' '+GLOBAL_DIR+' '+pol_name+' '+pol_shp)

        # os.system('ncbo -O -y multiply GRC_gfz_tot.nc ' + region_name + '.nc ' + region_name + '_tot.nc')
        # os.system('ncks -A -v time GRC_gfz_tot.nc ' + region_name + '_tot.nc')
        # os.system('ncwa -C -v lwe_thickness,lat,lon,time -a time ' + region_name + '_tot.nc AvgTot.nc')
        # os.system('ncwa -O -v lwe_thickness -a lat,lon ' + region_name + '_tot.nc teststp.nc')
        # os.system('ncap2 -A -s "where(lwe_thickness>-99998)lwe_thickness=1" ' + region_name + '_tot.nc tmptot.nc')
        # os.system('ncbo -O -y mlt tmptot.nc AvgTot.nc AvgTot.nc')
        # os.system('ncdiff -O teststp.nc AvgTot.nc ' + region_name + '_gfz_tot.nc')
        # os.system('ncwa -O -v lwe_thickness -a lat,lon ' + region_name + '_gfz_tot.nc ' + region_name + '_gfz_tot_ts.nc')
        # os.system('rm tmptot.nc')
        # os.system('rm teststp.nc')
        # os.system('rm AvgTot.nc')
        # os.system('rm ' + region_name + '_tot.nc')

        print('Subsetting GFZ Total Water Storage')

        return JsonResponse({"gfz_tot": "gfz_tot"})


def sub_gfz_gw(shapefile,region_name,GLOBAL_DIR,display_name,thredds_id):

        SHP_DIR = SHAPE_DIR


        SHP_DIR = os.path.join(SHP_DIR, '')

        temp_dir = tempfile.mkdtemp()
        for f in shapefile:
            f_name = f.name
            f_path = os.path.join(SHP_DIR, f_name)

            with open(f_path, 'wb') as f_local:
                f_local.write(f.read())

        for file in os.listdir(SHP_DIR):
            # Reading the shapefile only
            if file.endswith(".shp"):
                f_path = os.path.join(SHP_DIR, file)
                pol_shp = f_path
                pol_name = os.path.splitext(f_name)[0]


        os.system(SHELL_DIR+'subset_gfz_gw.sh '+region_name+' '+GLOBAL_DIR+' '+pol_name+' '+pol_shp)

        # os.system('cd ' + GLOBAL_DIR)
        # os.system('ncbo -O -y multiply GRC_gfz_gw.nc ' + region_name + '.nc ' + region_name + '_gw.nc')
        # os.system('ncks -A -v time GRC_gfz_gw.nc ' + region_name + '_gw.nc')
        # os.system('ncwa -C -v lwe_thickness,lat,lon,time -a time ' + region_name + '_gw.nc AvgGW.nc')
        # os.system('ncwa -O -v lwe_thickness -a lat,lon ' + region_name + '_gw.nc teststp.nc')
        # os.system('ncap2 -A -s "where(lwe_thickness>-99998)lwe_thickness=1" ' + region_name + '_gw.nc tmpgw.nc')
        # os.system('ncbo -O -y mlt tmpgw.nc AvgGW.nc AvgGW.nc')
        # os.system('ncdiff -O teststp.nc AvgGW.nc ' + region_name + '_gfz_gw.nc')
        # os.system('ncwa -O -v lwe_thickness -a lat,lon ' + region_name + '_gfz_gw.nc ' + region_name + '_gfz_gw_ts.nc')
        # os.system('rm tmpgw.nc')
        # os.system('rm teststp.nc')
        # os.system('rm AvgGW.nc')
        # os.system('rm ' + region_name + '_gw.nc')

        print('Subsetting GFZ Groundwater Storage')

        return JsonResponse({"gfz_gw": "gfz_gw"})


def sub_avg_tot(shapefile,region_name,GLOBAL_DIR,display_name,thredds_id):

        SHP_DIR = SHAPE_DIR


        SHP_DIR = os.path.join(SHP_DIR, '')

        temp_dir = tempfile.mkdtemp()
        for f in shapefile:
            f_name = f.name
            f_path = os.path.join(SHP_DIR, f_name)

            with open(f_path, 'wb') as f_local:
                f_local.write(f.read())

        for file in os.listdir(SHP_DIR):
            # Reading the shapefile only
            if file.endswith(".shp"):
                f_path = os.path.join(SHP_DIR, file)
                pol_shp = f_path
                pol_name = os.path.splitext(f_name)[0]


        os.system(SHELL_DIR+'subset_avg_tot.sh '+region_name+' '+GLOBAL_DIR+' '+pol_name+' '+pol_shp)

        # os.system('ncbo -O -y multiply GRC_avg_tot.nc ' + region_name + '.nc ' + region_name + '_tot.nc')
        # os.system('ncks -A -v time GRC_avg_tot.nc ' + region_name + '_tot.nc')
        # os.system('ncwa -C -v lwe_thickness,lat,lon,time -a time ' + region_name + '_tot.nc AvgTot.nc')
        # os.system('ncwa -O -v lwe_thickness -a lat,lon ' + region_name + '_tot.nc teststp.nc')
        # os.system('ncap2 -A -s "where(lwe_thickness>-99998)lwe_thickness=1" ' + region_name + '_tot.nc tmptot.nc')
        # os.system('ncbo -O -y mlt tmptot.nc AvgTot.nc AvgTot.nc')
        # os.system('ncdiff -O teststp.nc AvgTot.nc ' + region_name + '_avg_tot.nc')
        # os.system('ncwa -O -v lwe_thickness -a lat,lon ' + region_name + '_avg_tot.nc ' + region_name + '_avg_tot_ts.nc')
        # os.system('rm tmptot.nc')
        # os.system('rm teststp.nc')
        # os.system('rm AvgTot.nc')
        # os.system('rm ' + region_name + '_tot.nc')

        print('Subsetting AVG Total Storage')

        return JsonResponse({"avg_tot": "avg_tot"})


def sub_avg_gw(shapefile,region_name,GLOBAL_DIR,display_name,thredds_id):

        SHP_DIR = SHAPE_DIR


        SHP_DIR = os.path.join(SHP_DIR, '')

        temp_dir = tempfile.mkdtemp()
        for f in shapefile:
            f_name = f.name
            f_path = os.path.join(SHP_DIR, f_name)

            with open(f_path, 'wb') as f_local:
                f_local.write(f.read())

        for file in os.listdir(SHP_DIR):
            # Reading the shapefile only
            if file.endswith(".shp"):
                f_path = os.path.join(SHP_DIR, file)
                pol_shp = f_path
                pol_name = os.path.splitext(f_name)[0]


        os.system(SHELL_DIR+'subset_avg_gw.sh '+region_name+' '+GLOBAL_DIR+' '+pol_name+' '+pol_shp)

        # os.system('cd ' + GLOBAL_DIR)
        # os.system('ncbo -O -y multiply GRC_avg_gw.nc ' + region_name + '.nc ' + region_name + '_gw.nc')
        # os.system('ncks -A -v time GRC_avg_gw.nc ' + region_name + '_gw.nc')
        # os.system('ncwa -C -v lwe_thickness,lat,lon,time -a time ' + region_name + '_gw.nc AvgGW.nc')
        # os.system('ncwa -O -v lwe_thickness -a lat,lon ' + region_name + '_gw.nc teststp.nc')
        # os.system('ncap2 -A -s "where(lwe_thickness>-99998)lwe_thickness=1" ' + region_name + '_gw.nc tmpgw.nc')
        # os.system('ncbo -O -y mlt tmpgw.nc AvgGW.nc AvgGW.nc')
        # os.system('ncdiff -O teststp.nc AvgGW.nc ' + region_name + '_avg_gw.nc')
        # os.system('ncwa -O -v lwe_thickness -a lat,lon ' + region_name + '_avg_gw.nc ' + region_name + '_avg_gw_ts.nc')
        # os.system('rm tmpgw.nc')
        # os.system('rm teststp.nc')
        # os.system('rm AvgGW.nc')
        # os.system('rm ' + region_name + '_gw.nc')

        print('Subsetting AVG Groundwater Storage')

        return JsonResponse({"avg_gw": "avg_gw"})


def sub_sw(shapefile,region_name,GLOBAL_DIR,display_name,thredds_id):

        SHP_DIR = SHAPE_DIR


        SHP_DIR = os.path.join(SHP_DIR, '')

        temp_dir = tempfile.mkdtemp()
        for f in shapefile:
            f_name = f.name
            f_path = os.path.join(SHP_DIR, f_name)

            with open(f_path, 'wb') as f_local:
                f_local.write(f.read())

        for file in os.listdir(SHP_DIR):
            # Reading the shapefile only
            if file.endswith(".shp"):
                f_path = os.path.join(SHP_DIR, file)
                pol_shp = f_path
                pol_name = os.path.splitext(f_name)[0]


        os.system(SHELL_DIR+'subset_sw.sh '+region_name+' '+GLOBAL_DIR+' '+pol_name+' '+pol_shp)

        # os.system('cd ' + GLOBAL_DIR)
        # os.system('ncbo -O -y multiply GRC_jpl_sw.nc ' + region_name + '.nc ' + region_name + '_sw.nc')
        # os.system('ncks -A -v time GRC_jpl_tot.nc ' + region_name + '_sw.nc')
        # os.system('ncwa -C -v lwe_thickness,lat,lon,time -a time ' + region_name + '_sw.nc AvgSW.nc')
        # os.system('ncwa -O -v lwe_thickness -a lat,lon ' + region_name + '_sw.nc testswstp.nc')
        # os.system('ncap2 -A -s "where(lwe_thickness>-99998)lwe_thickness=1" ' + region_name + '_sw.nc tmpsw.nc')
        # os.system('ncbo -O -y mlt tmpsw.nc AvgSW.nc AvgSW.nc')
        # os.system('ncdiff -O testswstp.nc AvgSW.nc ' + region_name + '_sw.nc')
        # os.system('ncwa -O -v lwe_thickness -a lat,lon ' + region_name + '_sw.nc ' + region_name + '_sw_ts.nc')
        # os.system('rm tmpsw.nc')
        # os.system('rm testswstp.nc')
        # os.system('rm AvgSW.nc')

        print('Subsetting Surface Water Storage')

        return JsonResponse({"sw": "sw"})

def sub_soil(shapefile,region_name,GLOBAL_DIR,display_name,thredds_id):

        SHP_DIR = SHAPE_DIR


        SHP_DIR = os.path.join(SHP_DIR, '')

        temp_dir = tempfile.mkdtemp()
        for f in shapefile:
            f_name = f.name
            f_path = os.path.join(SHP_DIR, f_name)

            with open(f_path, 'wb') as f_local:
                f_local.write(f.read())

        for file in os.listdir(SHP_DIR):
            # Reading the shapefile only
            if file.endswith(".shp"):
                f_path = os.path.join(SHP_DIR, file)
                pol_shp = f_path
                pol_name = os.path.splitext(f_name)[0]


        os.system(SHELL_DIR+'subset_soil.sh '+region_name+' '+GLOBAL_DIR+' '+pol_name+' '+pol_shp)

        # os.system('cd ' + GLOBAL_DIR)
        # os.system('ncbo -O -y multiply GRC_jpl_soil.nc ' + region_name + '.nc ' + region_name + '_soil.nc')
        # os.system('ncks -A -v time GRC_jpl_tot.nc ' + region_name + '_soil.nc')
        # os.system('ncwa -C -v lwe_thickness,lat,lon,time -a time ' + region_name + '_soil.nc AvgSoil.nc')
        # os.system('ncwa -O -v lwe_thickness -a lat,lon ' + region_name + '_soil.nc testsoilstp.nc')
        # os.system('ncap2 -A -s "where(lwe_thickness>-99998)lwe_thickness=1" ' + region_name + '_soil.nc tmpsoil.nc')
        # os.system('ncbo -O -y mlt tmpsoil.nc AvgSoil.nc AvgSoil.nc')
        # os.system('ncdiff -O testsoilstp.nc AvgSoil.nc ' + region_name + '_soil.nc')
        # os.system('ncwa -O -v lwe_thickness -a lat,lon ' + region_name + '_soil.nc ' + region_name + '_soil_ts.nc')
        # os.system('rm tmpsoil.nc')
        # os.system('rm testsoilstp.nc')
        # os.system('rm AvgSoil.nc')

        print('Subsetting Soil Moisture Storage')

        return JsonResponse({"soil": "soil"})


def sub_file_cleanup(shapefile,region_name,GLOBAL_DIR,display_name,thredds_id):

        SHP_DIR = SHAPE_DIR


        SHP_DIR = os.path.join(SHP_DIR, '')

        temp_dir = tempfile.mkdtemp()
        for f in shapefile:
            f_name = f.name
            f_path = os.path.join(SHP_DIR, f_name)

            with open(f_path, 'wb') as f_local:
                f_local.write(f.read())

        for file in os.listdir(SHP_DIR):
            # Reading the shapefile only
            if file.endswith(".shp"):
                f_path = os.path.join(SHP_DIR, file)
                pol_shp = f_path
                pol_name = os.path.splitext(f_name)[0]


        os.system(SHELL_DIR+'file_cleanup.sh '+region_name+' '+GLOBAL_DIR+' '+pol_name+' '+pol_shp)

        # os.system('cd '+GLOBAL_DIR)
        # os.system('mkdir '+region_name)
        # os.system('mv ' + region_name + "_jpl_tot.nc " + GLOBAL_DIR + region_name + '/')
        # os.system('mv ' + region_name + "_jpl_gw.nc " + GLOBAL_DIR + region_name + '/')
        # os.system('mv ' + region_name + "_csr_tot.nc " + GLOBAL_DIR + region_name + '/')
        # os.system('mv ' + region_name + "_csr_gw.nc " + GLOBAL_DIR + region_name + '/')
        # os.system('mv ' + region_name + "_gfz_tot.nc " + GLOBAL_DIR + region_name + '/')
        # os.system('mv ' + region_name + "_gfz_gw.nc " + GLOBAL_DIR + region_name + '/')
        # os.system('mv ' + region_name + "_avg_tot.nc " + GLOBAL_DIR + region_name + '/')
        # os.system('mv ' + region_name + "_avg_gw.nc " + GLOBAL_DIR + region_name + '/')
        #
        # os.system('mv ' + region_name + "_jpl_tot_ts.nc " + GLOBAL_DIR + region_name + '/')
        # os.system('mv ' + region_name + "_jpl_gw_ts.nc " + GLOBAL_DIR + region_name + '/')
        # os.system('mv ' + region_name + "_csr_tot_ts.nc " + GLOBAL_DIR + region_name + '/')
        # os.system('mv ' + region_name + "_csr_gw_ts.nc " + GLOBAL_DIR + region_name + '/')
        # os.system('mv ' + region_name + "_gfz_tot_ts.nc " + GLOBAL_DIR + region_name + '/')
        # os.system('mv ' + region_name + "_gfz_gw_ts.nc " + GLOBAL_DIR + region_name + '/')
        # os.system('mv ' + region_name + "_avg_tot_ts.nc " + GLOBAL_DIR + region_name + '/')
        # os.system('mv ' + region_name + "_avg_gw_ts.nc " + GLOBAL_DIR + region_name + '/')
        #
        # os.system('cat '+region_name+'_sw.nc | tee '+GLOBAL_DIR+region_name+'/'+region_name+'_jpl_sw.nc '+GLOBAL_DIR+region_name+'/'+region_name+'_csr_sw.nc '+GLOBAL_DIR+region_name+'/'+region_name+'_gfz_sw.nc '+GLOBAL_DIR+region_name+'/'+region_name+'_avg_sw.nc> /dev/null')
        # os.system('cat '+region_name+'_soil.nc | tee '+GLOBAL_DIR+region_name+'/'+region_name+'_jpl_soil.nc '+GLOBAL_DIR+region_name+'/'+region_name+'_csr_soil.nc '+GLOBAL_DIR+region_name+'/'+region_name+'_gfz_soil.nc '+GLOBAL_DIR+region_name+'/'+region_name+'_avg_soil.nc> /dev/null')
        #
        # os.system('cat '+region_name+'_sw_ts.nc | tee '+GLOBAL_DIR+region_name+'/'+region_name+'_jpl_sw_ts.nc '+GLOBAL_DIR+region_name+'/'+region_name+'_csr_sw_ts.nc '+GLOBAL_DIR+region_name+'/'+region_name+'_gfz_sw_ts.nc '+GLOBAL_DIR+region_name+'/'+region_name+'_avg_sw_ts.nc> /dev/null')
        # os.system('cat '+region_name+'_soil_ts.nc | tee '+GLOBAL_DIR+region_name+'/'+region_name+'_jpl_soil_ts.nc '+GLOBAL_DIR+region_name+'/'+region_name+'_csr_soil_ts.nc '+GLOBAL_DIR+region_name+'/'+region_name+'_gfz_soil_ts.nc '+GLOBAL_DIR+region_name+'/'+region_name+'_avg_soil_ts.nc> /dev/null')
        #
        # os.system('rm '+region_name+'_sw')
        # os.system('rm '+region_name+'_soil')
        # os.system('rm '+region_name+'_sw_ts')
        # os.system('rm '+region_name+'_soil_ts')

        print('Copying and moving files')

        return JsonResponse({"cleanup": "cleanup"})


def sub_update_ps(shapefile,region_name,GLOBAL_DIR,display_name,thredds_id):

        SHP_DIR = SHAPE_DIR

        SHP_DIR = os.path.join(SHP_DIR, '')

        temp_dir = tempfile.mkdtemp()
        for f in shapefile:
            f_name = f.name
            f_path = os.path.join(SHP_DIR, f_name)

            with open(f_path, 'wb') as f_local:
                f_local.write(f.read())

        for file in os.listdir(SHP_DIR):
            # Reading the shapefile only
            if file.endswith(".shp"):
                f_path = os.path.join(SHP_DIR, file)
                pol_shp = f_path
                pol_name = os.path.splitext(f_name)[0]


        # *******************************************************************************
        # Read polygon shapefile
        # *******************************************************************************

        print('Read polygon shapefile')
        gbyos_pol_lay = fiona.open(pol_shp, 'r')
        IS_pol_tot = len(gbyos_pol_lay)
        print((' - The number of polygon features is: ' + str(IS_pol_tot)))

        # *******************************************************************************
        # Create spatial index for the bounds of each polygon feature
        # *******************************************************************************
        index = rtree.index.Index()
        shp_bounds = []

        def explode(coords):
            """Explode a GeoJSON geometry's coordinates object and yield coordinate tuples.
            As long as the input is conforming, the type of the geometry doesn't matter."""
            for e in coords:
                if isinstance(e, (float, int)):
                    yield coords
                    break
                else:
                    for f in explode(e):
                        yield f

        def bbox(f):
            x, y = list(zip(*list(explode(f['geometry']['coordinates']))))
            return min(x), min(y), max(x), max(y)
        def area_calc(f):
            gj = {'type': f['geometry']['type'], 'coordinates': f['geometry']['coordinates']}
            shape_area = area(gj)
            return shape_area

        for gbyos_pol_fea in gbyos_pol_lay:
            gbyos_pol_fid = int(gbyos_pol_fea['id'])
            # the first argument of index.insert has to be 'int', not 'long' or 'str'
            gbyos_pol_shy = shapely.geometry.shape(gbyos_pol_fea['geometry'])
            index.insert(gbyos_pol_fid, gbyos_pol_shy.bounds)
            shp_bounds.append(gbyos_pol_shy.bounds)
            bbox_val = bbox(gbyos_pol_fea)
            final_area = area_calc(gbyos_pol_fea)
            # creates an index between the feature ID and the bounds of that feature

        # *******************************************************************************
        # Add Region to Persistent Store DB
        # *******************************************************************************


        Session = Newgrace.get_persistent_store_database('gracefo_db', as_sessionmaker=True)
        session = Session()
        region = Region(thredds_id=thredds_id,display_name=display_name, latlon_bbox=str(bbox_val), reg_area= final_area)
        session.add(region)
        session.commit()
        session.close()

        for the_file in os.listdir(SHP_DIR):
            file_path = os.path.join(SHP_DIR, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                #elif os.path.isdir(file_path): shutil.rmtree(file_path)
            except Exception as e:
                print(e)

        return JsonResponse({"success": "success"})

