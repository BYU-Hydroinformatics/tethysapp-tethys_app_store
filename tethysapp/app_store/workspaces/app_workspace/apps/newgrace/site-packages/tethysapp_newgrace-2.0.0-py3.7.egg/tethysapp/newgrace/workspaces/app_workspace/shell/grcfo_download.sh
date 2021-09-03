#!/bin/bash

# $1 = get_global_netcdf_dir()
# $2 = Earth Data Username
# $3 = Earth Data Password


cd $1

rm .netrc
rm .urs_cookies
touch .netrc

wget --user=tmcstraw --password=dx1OVatDVDA4E66oNsLa -r -N -np -nH -nd -A "*.nc" https://podaac-tools.jpl.nasa.gov/drive/files/allData/tellus/L3/gracefo/land_mass/RL06/GFZ

ncrcat GRD-3_???????-???????_GRFO_GFZOP_BA01_0600_LND_v01.nc GRCFO_gfz_total.nc 

wget --user=tmcstraw --password=dx1OVatDVDA4E66oNsLa -r -N -np -nH -nd -A "*.nc" https://podaac-tools.jpl.nasa.gov/drive/files/allData/tellus/L3/gracefo/land_mass/RL06/JPL

ncrcat GRD-3_???????-???????_GRFO_JPLEM_BA01_0600_LND_v01.nc GRCFO_jpl_total.nc

wget --user=tmcstraw --password=dx1OVatDVDA4E66oNsLa -r -N -np -nH -nd -A "*.nc" https://podaac-tools.jpl.nasa.gov/drive/files/allData/tellus/L3/gracefo/land_mass/RL06/CSR

ncrcat GRD-3_???????-???????_GRFO_UTCSR_BA01_0600_LND_v01.nc GRCFO_csr_total.nc

rm GRD-3_???????-???????_GRFO_GFZOP_BA01_0600_LND_v01.nc
rm GRD-3_???????-???????_GRFO_JPLEM_BA01_0600_LND_v01.nc
rm GRD-3_???????-???????_GRFO_UTCSR_BA01_0600_LND_v01.nc

