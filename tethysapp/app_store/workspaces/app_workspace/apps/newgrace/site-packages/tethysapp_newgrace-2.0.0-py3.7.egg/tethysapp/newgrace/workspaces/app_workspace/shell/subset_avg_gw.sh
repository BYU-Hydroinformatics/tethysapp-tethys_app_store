#!/bin/bash

# $1 = region_name
# $2 = NETCDF_DIR
# $3 = shape file name w/o extension
# $4 = shape file name w/ extension.shp

cd $2
ext='.nc'
shapefile=$1$ext

tot=_tot.nc
soil=_soil.nc
sw=_sw.nc
gw=_gw.nc

total=$1$tot
surf=$1$sw
soilm=$1$soil
gdw=$1$gw

jpl=_jpl
csr=_csr
gfz=_gfz
avg=_avg

totts=_tot_ts.nc
soilts=_soil_ts.nc
swts=_sw_ts.nc
gwts=_gw_ts.nc

# Ensemble AVG of JPL, CSR, and GFZ Solutions

ncbo -O -y multiply GRC_jpl_gw.nc $shapefile $1$gw
ncks -A -v time GRC_avg_tot.nc $1$gw

#mean Calculations for avg groundwater storage
ncwa -C -v lwe_thickness,lat,lon,time -a time $1$gw AvgGW.nc
ncwa -O -v lwe_thickness -a lat,lon $1$gw testgwstp.nc
ncap2 -A -s "where(lwe_thickness>-99998)lwe_thickness=1" $1$gw tmpgw.nc
ncbo -O -y mlt tmpgw.nc AvgGW.nc AvgGW.nc
ncdiff testgwstp.nc AvgGW.nc $1$avg$gw
ncwa -O -v lwe_thickness -a lat,lon $1$avg$gw $1$avg$gwts


rm tmpgw.nc
rm testgwstp.nc
rm AvgGW.nc
rm $1$gw
