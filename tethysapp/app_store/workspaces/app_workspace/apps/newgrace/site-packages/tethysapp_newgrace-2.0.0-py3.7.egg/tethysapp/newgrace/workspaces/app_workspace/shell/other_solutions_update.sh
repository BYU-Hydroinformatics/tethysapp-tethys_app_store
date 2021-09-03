#!/bin/bash

# $1 = get_global_netcdf_dir()
# $2 = Earth Data Username
# $3 = Earth Data Password


cd $1

# CSR Processing

ncremap -i GRCFO_csr_total.nc -d GRC_jpl_tot.nc -o GRC_csr_tot_temp.nc

ncks -C -O -x -v time_bounds,area,gw GRC_csr_tot_temp.nc GRC_csr_tot_temp.nc

ncatted -O -a _FillValue,lwe_thickness,o,d,-99999.0 GRC_csr_tot_temp.nc

ncks -O -3 GRC_csr_tot_temp.nc GRC_csr_tot_temp.nc

ncflint -A --fix_rec_crd -w 100,0.0 GRC_csr_tot_temp.nc GRC_csr_tot_temp.nc GRC_csr_tot_temp.nc


ncdiff -O GRC_csr_tot_temp.nc GRC_csr_sw_temp.nc GRC_csr_gw1.nc
ncdiff -O GRC_csr_gw1.nc GRC_csr_soil_temp.nc GRC_csr_gw_temp.nc

ncks -C -O -x -v time_bounds,area,gw GRC_csr_gw_temp.nc GRC_csr_gw_temp.nc

rm GRC_csr_gw1.nc
rm PET0.RegridWeightGen.Log


# GFZ Processing

ncremap -i GRCFO_gfz_total.nc -d GRC_jpl_tot.nc -o GRC_gfz_tot_temp.nc

ncks -C -O -x -v time_bounds,area,gw GRC_gfz_tot_temp.nc GRC_gfz_tot_temp.nc

ncatted -O -a _FillValue,lwe_thickness,o,d,-99999.0 GRC_gfz_tot_temp.nc

ncks -O -3 GRC_gfz_tot_temp.nc GRC_gfz_tot_temp.nc

ncflint -A --fix_rec_crd -w 100,0.0 GRC_gfz_tot_temp.nc GRC_gfz_tot_temp.nc GRC_gfz_tot_temp.nc


ncdiff -O GRC_gfz_tot_temp.nc GRC_gfz_sw_temp.nc GRC_gfz_gw1.nc
ncdiff -O GRC_gfz_gw1.nc GRC_gfz_soil_temp.nc GRC_gfz_gw_temp.nc

ncks -C -O -x -v time_bounds,area,gw GRC_gfz_gw_temp.nc GRC_gfz_soil_temp.nc

rm GRC_gfz_gw1.nc
rm PET0.RegridWeightGen.Log


# AVG Processing

ncbo --op_typ=add GRC_jpl_tot_temp.nc GRC_csr_tot_temp.nc GRC_avg1_tot.nc

ncbo --op_typ=add GRC_avg1_tot.nc GRC_gfz_tot_temp.nc GRC_avg_tot_temp.nc

ncks -O -3 GRC_avg_tot_temp.nc GRC_avg_tot_temp.nc

ncflint -A --fix_rec_crd -w 0.3333,0.0 GRC_avg_tot_temp.nc GRC_avg_tot_temp.nc GRC_avg_tot_temp.nc




ncbo --op_typ=add GRC_jpl_gw_temp.nc GRC_csr_gw_temp.nc GRC_avg1_gw.nc

ncbo --op_typ=add GRC_avg1_gw.nc GRC_gfz_gw_temp.nc GRC_avg_gw_temp.nc

ncks -O -3 GRC_avg_gw_temp.nc GRC_avg_gw_temp.nc

ncflint -A --fix_rec_crd -w 0.3333,0.0 GRC_avg_gw_temp.nc GRC_avg_gw_temp.nc GRC_avg_gw_temp.nc


rm GRC_avg1_gw.nc
rm GRC_avg1_tot.nc




ncrcat -O GRC_jpl_tot.nc GRC_jpl_tot_temp.nc GRC_jpl_tot.nc

ncrcat -O GRC_jpl_gw.nc GRC_jpl_gw_temp.nc GRC_jpl_gw.nc

ncrcat -O GRC_jpl_sw.nc GRC_jpl_sw_temp.nc GRC_jpl_sw.nc

ncrcat -O GRC_jpl_soil.nc GRC_jpl_soil_temp.nc GRC_jpl_soil.nc


ncrcat -O GRC_csr_tot.nc GRC_csr_tot_temp.nc GRC_csr_tot.nc

ncrcat -O GRC_csr_gw.nc GRC_csr_gw_temp.nc GRC_csr_gw.nc

ncrcat -O GRC_csr_sw.nc GRC_csr_sw_temp.nc GRC_csr_sw.nc

ncrcat -O GRC_csr_soil.nc GRC_csr_soil_temp.nc GRC_csr_soil.nc



ncrcat -O GRC_gfz_tot.nc GRC_gfz_tot_temp.nc GRC_gfz_tot.nc

ncrcat -O GRC_gfz_gw.nc GRC_gfz_gw_temp.nc GRC_gfz_gw.nc

ncrcat -O GRC_gfz_sw.nc GRC_gfz_sw_temp.nc GRC_gfz_sw.nc

ncrcat -O GRC_gfz_soil.nc GRC_gfz_soil_temp.nc GRC_gfz_soil.nc



ncrcat -O GRC_avg_tot.nc GRC_avg_tot_temp.nc GRC_avg_tot.nc

ncrcat -O GRC_avg_gw.nc GRC_avg_gw_temp.nc GRC_avg_gw.nc

ncrcat -O GRC_avg_sw.nc GRC_avg_sw_temp.nc GRC_avg_sw.nc

ncrcat -O GRC_avg_soil.nc GRC_avg_soil_temp.nc GRC_avg_soil.nc





