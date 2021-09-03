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



ncbo -O -y multiply GRC_jpl_soil.nc $shapefile $1$soil
ncks -A -v time GRC_jpl_tot.nc $1$soil

#mean Calculations for soil moisture storage
ncwa -C -v lwe_thickness,lat,lon,time -a time $1$soil AvgSoil.nc
ncwa -O -v lwe_thickness -a lat,lon $1$soil testsoilstp.nc
ncap2 -A -s "where(lwe_thickness>-99998)lwe_thickness=1" $1$soil tmpsoil.nc
ncbo -O -y mlt tmpsoil.nc AvgSoil.nc AvgSoil.nc
ncdiff -O testsoilstp.nc AvgSoil.nc $1$soil
ncwa -O -v lwe_thickness -a lat,lon $1$soil $1$soilts


rm tmpsoil.nc
rm testsoilstp.nc
rm AvgSoil.nc

