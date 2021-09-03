#!/bin/bash

# $1 = region_name
# $2 = NETCDF_DIR
# $3 = shape file name w/o extension
# $4 = shape file name w/ extension.shp

cd $2
ext='.nc'
shapefile=$1$ext
echo $shapefile
gdal_rasterize -burn 1 -l $3 -of netcdf -te -180 -60 180 90 -co "FORMAT=NC4" -tr 0.25 0.25 $4 $shapefile
ncatted -a _FillValue,Band1,o,d,-99999.0 $shapefile
ncrename -O -v Band1,lwe_thickness $shapefile 
ncks -O -v lwe_thickness --msa -d lon,0.0,180.0 -d lon,-180.0,-0.125 $shapefile $shapefile
ncap2 -O -s "where(lon<0) lon=lon+360" $shapefile $shapefile

