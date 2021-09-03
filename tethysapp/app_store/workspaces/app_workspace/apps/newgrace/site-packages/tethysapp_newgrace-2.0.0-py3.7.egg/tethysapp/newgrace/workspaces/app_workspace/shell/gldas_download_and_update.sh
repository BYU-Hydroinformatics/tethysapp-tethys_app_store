#!/bin/bash

# $1 = get_global_netcdf_dir()
# $2 = Earth Data Username
# $3 = Earth Data Password


cd $1

rm .netrc
rm .urs_cookies
touch .netrc
echo “machine urs.earthdata.nasa.gov login gracedata1 password GRACEData1” >> .netrc
chmod 0600 .netrc
touch .urs_cookies
wget --content-disposition --load-cookies ~/.urs_cookies --save-cookies ~/.urs_cookies --auth-no-challenge=on --keep-session-cookies --content-disposition -i GLDASlinks.txt

ncrcat GLDAS_NOAH025_3H.A????????.????.021.nc4.SUB.nc4 gldas_grace_dates.nc

ncdiff -O gldas_grace_dates.nc base_mean.nc anomaly.nc

ncap2 -A -s "sw=CanopInt_inst+Qs_acc+Qsb_acc+Qsm_acc+SWE_inst" anomaly.nc anomaly.nc

ncap2 -A -s "soil=RootMoist_inst+SoilMoi0_10cm_inst+SoilMoi100_200cm_inst+SoilMoi10_40cm_inst+SoilMoi40_100cm_inst" anomaly.nc anomaly.nc

ncks -C -O -x -v CanopInt_inst,Qs_acc,Qsb_acc,Qsm_acc,RootMoist_inst,SoilMoi0_10cm_inst,SoilMoi100_200cm_inst,SoilMoi10_40cm_inst,SoilMoi40_100cm_inst,SWE_inst anomaly.nc anomaly.nc

ncatted -O -a _FillValue,soil,o,d,-99999.0 anomaly.nc
ncatted -O -a _FillValue,sw,o,d,-99999.0 anomaly.nc

ncatted -O -a missing_value,soil,d,, anomaly.nc
ncatted -O -a missing_value,sw,d,, anomaly.nc

ncatted -O -a standard_name,soil,d,, anomaly.nc
ncatted -O -a standard_name,sw,d,, anomaly.nc

ncatted -O -a vmax,soil,d,, anomaly.nc
ncatted -O -a vmax,sw,d,, anomaly.nc

ncatted -O -a vmin,soil,d,, anomaly.nc
ncatted -O -a vmin,sw,d,, anomaly.nc

ncatted -O -a _ChunkSizes,,d,, anomaly.nc
ncatted -O -a _ChunkSizes,,d,, anomaly.nc

ncatted -O -a units,soil,o,c,cm anomaly.nc
ncatted -O -a units,sw,o,c,cm anomaly.nc

ncatted -O -a cell_methods,soil,d,, anomaly.nc
ncatted -O -a cell_methods,sw,d,, anomaly.nc

ncatted -O -a cell_measures,soil,c,c,area:area anomaly.nc
ncatted -O -a cell_measures,sw,c,c,area:area anomaly.nc

ncap2 -O -s "lat=double(lat)" anomaly.nc anomaly.nc
ncap2 -O -s "lon=double(lon)" anomaly.nc anomaly.nc

ncatted -O -a valid_min,lon,d,, anomaly.nc
ncatted -O -a valid_max,lon,d,, anomaly.nc
ncatted -O -a bounds,lon,d,, anomaly.nc


ncatted -O -a valid_min,lat,d,, anomaly.nc
ncatted -O -a valid_max,lat,d,, anomaly.nc
ncatted -O -a bounds,lat,d,, anomaly.nc

ncks -O -v soil,sw --msa -d lon,0.0,180.0 -d lon,-180.0,-0.125 anomaly.nc anomaly.nc
ncap2 -O -s "where(lon<0) lon=lon+360" anomaly.nc anomaly.nc

ncks -C -O -x -v time_bnds anomaly.nc anomaly.nc


ncremap -i GRCFO_jpl_total.nc -d GRC_jpl_tot.nc -o GRC_jpl_tot_temp.nc

ncatted -O -a _FillValue,lwe_thickness,o,d,-99999.0 GRC_jpl_tot_temp.nc

ncks -A -v lat,lon,lon_bnds,lat_bnds,time,time_bounds GRC_jpl_tot_temp.nc anomaly.nc

ncks -C -O -v lat,lat_bnds,lon,lon_bnds,time,soil,time_bounds anomaly.nc GRC_jpl_soil_temp.nc
ncrename -O -v soil,lwe_thickness GRC_jpl_soil_temp.nc
ncks -C -O -x -v time_bounds GRC_jpl_soil_temp.nc GRC_jpl_soil_temp.nc


ncks -C -O -v lat,lat_bnds,lon,lon_bnds,time,sw,time_bounds anomaly.nc GRC_jpl_sw_temp.nc
ncrename -O -v sw,lwe_thickness GRC_jpl_sw_temp.nc
ncks -C -O -x -v time_bounds GRC_jpl_sw_temp.nc GRC_jpl_sw_temp.nc

ncflint -A --fix_rec_crd -w 0.1,0.0 GRC_jpl_sw_temp.nc GRC_jpl_sw_temp.nc GRC_jpl_sw_temp.nc

ncflint -A --fix_rec_crd -w 0.1,0.0 GRC_jpl_soil_temp.nc GRC_jpl_soil_temp.nc GRC_jpl_soil_temp.nc

ncks -O -3 GRC_jpl_tot_temp.nc GRC_jpl_tot_temp.nc

ncflint -A --fix_rec_crd -w 100.0,0.0 GRC_jpl_tot_temp.nc GRC_jpl_tot_temp.nc GRC_jpl_tot_temp.nc

ncks -C -O -x -v time_bounds,area,gw GRC_jpl_tot_temp.nc GRC_jpl_tot_temp.nc


ncdiff -O GRC_jpl_tot_temp.nc GRC_jpl_sw_temp.nc GRC_jpl_gw1.nc
ncdiff -O GRC_jpl_gw1.nc GRC_jpl_soil_temp.nc GRC_jpl_gw_temp.nc

rm GRC_jpl_gw1.nc
rm PET0.RegridWeightGen.Log
rm anomaly.nc



cat GRC_jpl_sw_temp.nc | tee GRC_csr_sw_temp.nc GRC_gfz_sw_temp.nc GRC_avg_sw_temp.nc> /dev/null

cat GRC_jpl_soil_temp.nc | tee GRC_csr_soil_temp.nc GRC_gfz_soil_temp.nc GRC_avg_soil_temp.nc> /dev/null



