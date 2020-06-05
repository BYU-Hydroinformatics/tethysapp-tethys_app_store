#!/bin/bash

echo "Running Conda Install"
conda install -y -S -q -c $2 $1
echo "Conda Install Complete"