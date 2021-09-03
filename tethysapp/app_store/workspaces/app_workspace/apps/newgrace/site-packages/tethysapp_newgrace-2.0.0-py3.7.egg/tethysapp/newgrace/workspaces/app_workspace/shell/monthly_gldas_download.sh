#!/bin/bash

# $1 = get_global_netcdf_dir()
# $2 = Earth Data Username
# $3 = Earth Data Password

cd $1

rm .netrc
rm .urs_cookies
touch .netrc
echo “machine urs.earthdata.nasa.gov login gracedata1 password GRACEData1” >> .netrc
chmod 0600 .netrc
touch .urs_cookies
wget --content-disposition --load-cookies ~/.urs_cookies --save-cookies ~/.urs_cookies --auth-no-challenge=on --keep-session-cookies --content-disposition -i monthlyGLDASlinks.txt