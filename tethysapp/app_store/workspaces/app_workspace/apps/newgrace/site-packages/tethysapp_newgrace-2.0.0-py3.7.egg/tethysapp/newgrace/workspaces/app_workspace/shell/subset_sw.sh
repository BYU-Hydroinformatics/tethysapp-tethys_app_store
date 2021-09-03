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



ncbo -O -y multiply GRC_jpl_sw.nc $shapefile $1$sw
ncks -A -v time GRC_jpl_tot.nc $1$sw

#mean Calculations for surface water storage
ncwa -C -v lwe_thickness,lat,lon,time -a time $1$sw AvgSW.nc
ncwa -O -v lwe_thickness -a lat,lon $1$sw testswstp.nc
ncap2 -A -s "where(lwe_thickness>-99998)lwe_thickness=1" $1$sw tmpsw.nc
ncbo -O -y mlt tmpsw.nc AvgSW.nc AvgSW.nc
ncdiff -O testswstp.nc AvgSW.nc $1$sw
ncwa -O -v lwe_thickness -a lat,lon $1$sw $1$swts


rm tmpsw.nc
rm testswstp.nc
rm AvgSW.nc

