#!/bin/bash

echo "Running Conda Install"
conda install -y --freeze-installed -q -c $2 -c tethysplatform -c conda-forge $1
echo "Conda Install Complete"