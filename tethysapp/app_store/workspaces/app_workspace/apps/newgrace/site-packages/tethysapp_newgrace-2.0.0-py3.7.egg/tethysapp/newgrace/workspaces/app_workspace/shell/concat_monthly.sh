#!/bin/bash

# $1 = get_global_netcdf_dir()


cd $1

ncrcat GLDAS_NOAH025_M.A??????.021.nc4.SUB.nc4 monthly.nc

ncwa -a time monthly.nc base_mean.nc

ncrcat GLDAS_NOAH025_3H.A????????.????.021.nc4.SUB.nc4 gldas_grace_dates.nc

ncdiff -O gldas_grace_dates.nc base_mean.nc anomaly.nc

ncap2 -A -s "sw=CanopInt_inst+Qs_acc+Qsb_acc+Qsm_acc+SWE_inst" anomaly.nc anomaly.nc

ncap2 -A -s "soil=RootMoist_inst+SoilMoi0_10cm_inst+SoilMoi100_200cm_inst+SoilMoi10_40cm_inst+SoilMoi40_100cm_inst" anomaly.nc anomaly.nc

ncks -C -O -x -v CanopInt_inst,Qs_acc,Qsb_acc,Qsm_acc,RootMoist_inst,SoilMoi0_10cm_inst,SoilMoi100_200cm_inst,SoilMoi10_40cm_inst,SoilMoi40_100cm_inst,SWE_inst anomaly.nc anomaly.nc

#ncremap -i GRC_jpl_tot_test.nc -d anomaly.nc -o GRC_jpl_tot.nc

#ncks -C -O -x -v area,gw,lat_bnds,lon_bnds GRC_jpl_tot.nc GRC_jpl_tot.nc

#ncatted -O -a _FillValue,lwe_thickness,o,d,-99999.0 GRC_jpl_tot.nc

#ncatted -O -a _FillValue,soil,o,d,-99999.0 anomaly.nc
#ncatted -O -a _FillValue,sw,o,d,-99999.0 anomaly.nc

#ncatted -O -a missing_value,soil,d,, anomaly.nc
#ncatted -O -a missing_value,sw,d,, anomaly.nc

#ncatted -O -a standard_name,soil,d,, anomaly.nc
#ncatted -O -a standard_name,sw,d,, anomaly.nc

#ncatted -O -a vmax,soil,d,, anomaly.nc
#ncatted -O -a vmax,sw,d,, anomaly.nc

#ncatted -O -a vmin,soil,d,, anomaly.nc
#ncatted -O -a vmin,sw,d,, anomaly.nc

#ncatted -O -a _ChunkSizes,,d,, anomaly.nc
#ncatted -O -a _ChunkSizes,,d,, anomaly.nc

#ncatted -O -a units,soil,o,c,cm anomaly.nc
#ncatted -O -a units,sw,o,c,cm anomaly.nc

#ncatted -O -a cell_methods,soil,d,, anomaly.nc
#ncatted -O -a cell_methods,sw,d,, anomaly.nc

#ncatted -O -a cell_measures,soil,c,c,area:area anomaly.nc
#ncatted -O -a cell_measures,sw,c,c,area:area anomaly.nc

#ncap2 -O -s "lat=double(lat)" anomaly.nc anomaly.nc
#ncap2 -O -s "lon=double(lon)" anomaly.nc anomaly.nc

#ncks -O -v lwe_thickness --msa -d lon,0.0,180.0 -d lon,-180.0,-0.125 GRC_jpl_tot.nc GRC_jpl_tot.nc
#ncap2 -O -s "where(lon<0) lon=lon+360" GRC_jpl_tot.nc GRC_jpl_tot.nc

#ncks -O -v soil,sw --msa -d lon,0.0,180.0 -d lon,-180.0,-0.125 anomaly.nc anomaly.nc
#ncap2 -O -s "where(lon<0) lon=lon+360" anomaly.nc anomaly.nc


#ncks -A -v lat,lon,time GRC_jpl_tot.nc anomaly.nc
#ncks -C -O -x -v time_bnds anomaly.nc anomaly.nc


#ncks -C -O -v lat,lon,time,soil anomaly.nc GRC_jpl_soil.nc
#ncrename -O -v soil,lwe_thickness GRC_jpl_soil.nc


#ncks -C -O -v lat,lon,time,sw anomaly.nc GRC_jpl_sw.nc
#ncrename -O -v sw,lwe_thickness GRC_jpl_sw.nc


#ncdiff -O GRC_jpl_tot.nc GRC_jpl_sw.nc GRC_jpl_gw1.nc
#ncdiff -O GRC_jpl_gw1.nc GRC_jpl_soil.nc GRC_jpl_gw.nc

#rm GRC_jpl_gw1.nc
#rm PET0.RegridWeightGen.Log
#rm anomaly.nc







