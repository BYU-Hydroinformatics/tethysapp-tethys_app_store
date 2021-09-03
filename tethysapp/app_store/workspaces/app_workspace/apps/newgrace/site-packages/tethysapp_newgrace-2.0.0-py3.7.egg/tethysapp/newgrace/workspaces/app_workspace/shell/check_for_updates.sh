#!/bin/bash

# $1 = get_global_netcdf_dir()
# $2 = Earth Data Username
# $3 = Earth Data Password


cd $1

rm .netrc
rm .urs_cookies
touch .netrc

wget --user=tmcstraw --password=44UaeAOUUoTSkPZPpNAq -r -N -np -nH -nd -A "*.nc" https://podaac-tools.jpl.nasa.gov/drive/files/allData/tellus/L3/gracefo/land_mass/RL06/v03/JPL/

