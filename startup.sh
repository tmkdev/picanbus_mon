#!/bin/bash
cd /home/pi/picanbus_mon

if [ -f "/home/pi/RUNDISP" ]; then 
    export CANBUS=can0
    echo $CANBUS >> /home/pi/runlog.log

    /usr/bin/python3 /home/pi/picanbus_mon/cardisp/hs_scan.py >> /home/pi/runlog.log 2>&1 

else
  echo "Not starting app.." >> /home/pi/runlog.log
  exit 1
fi