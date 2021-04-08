#!/bin/bash

while :
do
  date
  echo "Start Loop"
  python3 nut-influxdb-exporter.py
  RET=$?
  if [ ${RET} -ne 0 ];
  then
    echo "Exit status not 0"
    echo "Sleep 120"
    sleep 120
  fi
  date
  echo "Sleep 60"
  sleep 60
done
