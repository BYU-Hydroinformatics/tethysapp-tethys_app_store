#!/bin/bash

RESTART_DIR="/home/rafael/.tethys/restart"
# RESTART_DIR="/Users/rohitfun/git/tethysdev/warehouse/test"

nohup sh -c 'while true; do
	if [ -f "$RESTART_DIR/restart" ]; then
	    echo "Restarting"
	    unlink $RESTART_DIR/restart
	    supervisorctl restart all
	fi
  sleep 5;
done
' > /dev/null &
