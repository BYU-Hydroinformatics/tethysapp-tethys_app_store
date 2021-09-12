#!/bin/bash

RESTART_DIR="/Users/rohitfun/git/tethysdev/warehouse/test"

if [ -f "$RESTART_DIR/restart" ]; then
    echo "Restarting"
    # supervisorctl restart all
    unlink $RESTART_DIR/restart
fi