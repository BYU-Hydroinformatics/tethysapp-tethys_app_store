#!/bin/bash

echo "Running Mamba remove"
mamba remove -y --force -c tethysplatform --override-channels $1
echo "Mamba Remove Complete"
