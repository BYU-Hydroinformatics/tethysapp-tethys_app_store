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

rm $shapefile

s='/'
d=$1$s


mkdir $1

mv $1$jpl$tot $2$d 
mv $1$jpl$gw $2$d
mv $1$csr$tot $2$d
mv $1$csr$gw $2$d
mv $1$gfz$tot $2$d
mv $1$gfz$gw $2$d
mv $1$avg$tot $2$d
mv $1$avg$gw $2$d

mv $1$jpl$totts $2$d 
mv $1$jpl$gwts $2$d
mv $1$csr$totts $2$d
mv $1$csr$gwts $2$d
mv $1$gfz$totts $2$d
mv $1$gfz$gwts $2$d
mv $1$avg$totts $2$d
mv $1$avg$gwts $2$d

cat $1$sw | tee $2$d$1$jpl$sw $2$d$1$csr$sw $2$d$1$gfz$sw $2$d$1$avg$sw> /dev/null

cat $1$soil | tee $2$d$1$jpl$soil $2$d$1$csr$soil $2$d$1$gfz$soil $2$d$1$avg$soil> /dev/null

cat $1$swts | tee $2$d$1$jpl$swts $2$d$1$csr$swts $2$d$1$gfz$swts $2$d$1$avg$swts> /dev/null

cat $1$soilts | tee $2$d$1$jpl$soilts $2$d$1$csr$soilts $2$d$1$gfz$soilts $2$d$1$avg$soilts> /dev/null

rm $1$sw
rm $1$soil

rm $1$swts
rm $1$soilts