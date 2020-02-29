#!/bin/bash

cd /home/pi/picanbus_mon
export CANBUS=can0

sudo /usr/bin/python3 /home/pi/picanbus_mon/cardisp/hs_scan.py > /home/pi/runlog.log 2>&1 &

