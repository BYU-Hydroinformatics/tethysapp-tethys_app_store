#!/bin/bash

echo "Running Mamba Install"
# mamba install -y --freeze-installed -q -c $2 -c tethysplatform -c conda-forge $1
mamba install -y -q -c $2 -c tethysplatform -c conda-forge $1

echo "Mamba Install Complete"