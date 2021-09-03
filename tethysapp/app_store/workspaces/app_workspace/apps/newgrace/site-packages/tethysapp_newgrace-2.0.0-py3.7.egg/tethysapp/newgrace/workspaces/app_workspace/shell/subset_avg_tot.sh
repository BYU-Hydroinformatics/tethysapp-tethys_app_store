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

ncbo -O -y multiply GRC_avg_tot.nc $shapefile $1$tot
ncks -A -v time GRC_avg_tot.nc $1$tot

#mean Calculations for avg total water storage
ncwa -C -v lwe_thickness,lat,lon,time -a time $1$tot AvgTot.nc
ncwa -O -v lwe_thickness -a lat,lon $1$tot teststp.nc
ncap2 -A -s "where(lwe_thickness>-99998)lwe_thickness=1" $1$tot tmptot.nc
ncbo -O -y mlt tmptot.nc AvgTot.nc AvgTot.nc
ncdiff teststp.nc AvgTot.nc $1$avg$tot
ncwa -O -v lwe_thickness -a lat,lon $1$avg$tot $1$avg$totts


rm tmptot.nc
rm teststp.nc
rm AvgTot.nc
rm $1$tot