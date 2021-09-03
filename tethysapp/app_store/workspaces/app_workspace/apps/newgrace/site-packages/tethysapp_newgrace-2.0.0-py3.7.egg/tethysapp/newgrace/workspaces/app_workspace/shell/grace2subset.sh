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


# JPL


ncbo -O -y multiply GRC_jpl_tot.nc $shapefile $1$tot
ncks -A -v time GRC_jpl_tot.nc $1$tot
ncbo -O -y multiply GRC_jpl_sw.nc $shapefile $1$sw
ncks -A -v time GRC_jpl_tot.nc $1$sw
ncbo -O -y multiply GRC_jpl_soil.nc $shapefile $1$soil
ncks -A -v time GRC_jpl_tot.nc $1$soil
ncbo -O -y multiply GRC_jpl_gw.nc $shapefile $1$gw
ncks -A -v time GRC_jpl_tot.nc $1$gw


#mean Calculations for jpl total water storage
ncwa -C -v lwe_thickness,lat,lon,time -a time $1$tot AvgTot.nc
ncwa -O -v lwe_thickness -a lat,lon $1$tot teststp.nc
ncap2 -A -s "where(lwe_thickness>-99998)lwe_thickness=1" $1$tot tmptot.nc
ncbo -O -y mlt tmptot.nc AvgTot.nc AvgTot.nc
ncdiff -O teststp.nc AvgTot.nc $1$jpl$tot
ncwa -O -v lwe_thickness -a lat,lon $1$jpl$tot $1$jpl$totts

rm tmptot.nc
rm teststp.nc
rm AvgTot.nc
rm $1$tot


#mean Calculations for jpl groundwater storage
ncwa -C -v lwe_thickness,lat,lon,time -a time $1$gw AvgGW.nc
ncwa -O -v lwe_thickness -a lat,lon $1$gw testgwstp.nc
ncap2 -A -s "where(lwe_thickness>-99998)lwe_thickness=1" $1$gw tmpgw.nc
ncbo -O -y mlt tmpgw.nc AvgGW.nc AvgGW.nc
ncdiff testgwstp.nc AvgGW.nc $1$jpl$gw
ncwa -O -v lwe_thickness -a lat,lon $1$jpl$gw $1$jpl$gwts


rm tmpgw.nc
rm testgwstp.nc
rm AvgGW.nc
rm $1$gw


# CSR

ncbo -O -y multiply GRC_csr_tot.nc $shapefile $1$tot
ncks -A -v time GRC_csr_tot.nc $1$tot
ncbo -O -y multiply GRC_csr_gw.nc $shapefile $1$gw
ncks -A -v time GRC_csr_tot.nc $1$gw


#mean Calculations for csr total water storage
ncwa -C -v lwe_thickness,lat,lon,time -a time $1$tot AvgTot.nc
ncwa -O -v lwe_thickness -a lat,lon $1$tot teststp.nc
ncap2 -A -s "where(lwe_thickness>-99998)lwe_thickness=1" $1$tot tmptot.nc
ncbo -O -y mlt tmptot.nc AvgTot.nc AvgTot.nc
ncdiff teststp.nc AvgTot.nc $1$csr$tot
ncwa -O -v lwe_thickness -a lat,lon $1$csr$tot $1$csr$totts


rm tmptot.nc
rm teststp.nc
rm AvgTot.nc
rm $1$tot


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


#mean Calculations for csr groundwater storage
ncwa -C -v lwe_thickness,lat,lon,time -a time $1$gw AvgGW.nc
ncwa -O -v lwe_thickness -a lat,lon $1$gw testgwstp.nc
ncap2 -A -s "where(lwe_thickness>-99998)lwe_thickness=1" $1$gw tmpgw.nc
ncbo -O -y mlt tmpgw.nc AvgGW.nc AvgGW.nc
ncdiff testgwstp.nc AvgGW.nc $1$csr$gw
ncwa -O -v lwe_thickness -a lat,lon $1$csr$gw $1$csr$gwts


rm tmpgw.nc
rm testgwstp.nc
rm AvgGW.nc
rm $1$gw


# GFZ

ncbo -O -y multiply GRC_gfz_tot.nc $shapefile $1$tot
ncks -A -v time GRC_gfz_tot.nc $1$tot
ncbo -O -y multiply GRC_gfz_gw.nc $shapefile $1$gw
ncks -A -v time GRC_gfz_tot.nc $1$gw


#mean Calculations for gfz total water storage
ncwa -C -v lwe_thickness,lat,lon,time -a time $1$tot AvgTot.nc
ncwa -O -v lwe_thickness -a lat,lon $1$tot teststp.nc
ncap2 -A -s "where(lwe_thickness>-99998)lwe_thickness=1" $1$tot tmptot.nc
ncbo -O -y mlt tmptot.nc AvgTot.nc AvgTot.nc
ncdiff teststp.nc AvgTot.nc $1$gfz$tot
ncwa -O -v lwe_thickness -a lat,lon $1$gfz$tot $1$gfz$totts


rm tmptot.nc
rm teststp.nc
rm AvgTot.nc
rm $1$tot


#mean Calculations for gfz groundwater storage
ncwa -C -v lwe_thickness,lat,lon,time -a time $1$gw AvgGW.nc
ncwa -O -v lwe_thickness -a lat,lon $1$gw testgwstp.nc
ncap2 -A -s "where(lwe_thickness>-99998)lwe_thickness=1" $1$gw tmpgw.nc
ncbo -O -y mlt tmpgw.nc AvgGW.nc AvgGW.nc
ncdiff testgwstp.nc AvgGW.nc $1$gfz$gw
ncwa -O -v lwe_thickness -a lat,lon $1$gfz$gw $1$gfz$gwts


rm tmpgw.nc
rm testgwstp.nc
rm AvgGW.nc
rm $1$gw


# Ensemble AVG of JPL, CSR, and GFZ Solutions

ncbo -O -y multiply GRC_avg_tot.nc $shapefile $1$tot
ncks -A -v time GRC_avg_tot.nc $1$tot
ncbo -O -y multiply GRC_jpl_gw.nc $shapefile $1$gw
ncks -A -v time GRC_avg_tot.nc $1$gw


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