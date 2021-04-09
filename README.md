# nut-influxdbv2

This is a docker container that pulls data from a NUT server and pushed to InfluxDB. Based on work of mihai-cindea [https://github.com/mihai-cindea/nut-influxdb-exporter)

## Changes
Updated for InfluxDBv2. Changed outputted values. Poll  multiple NUT servers.


## Roadmap

## NUT Servers Accessories
- Get IP address of NUT servers
- Create list of IPs: ['IP1','IP2', ...]
- Create list of hostnames (mapped to hosts in Influx): ['Host1','Host2', ...]

## InfluxDBv2 Setup
Setup InfluxDBv2, create bucket and create a token with write permissions for bucket.

## Docker Setup
```
$ docker run -d \
 -e NUT_IP_LIST="['IP1','IP2',...]" \
 -e NUT_HOST_LIST="['<Host1>','<Host2>',...]" \
 -e NUT_PORT="<NUT Port>" \
 -e NUT_PASSWORD="<NUT password>" \
 -e NUT_USERNAME="<NUT username>" \
 -e NUT_UPSNAME="<NUT UPS Name>" \
 -e INFLUXDB2_HOST="<INFLUXDBv2 SERVER>" \
 -e INFLUXDB2_PORT="8086" \
 -e INFLUXDB2_ORG="" \
 -e INFLUXDB2_TOKEN="" \
 -e INFLUXDB2_BUCKET="" \
 --name "nut-influxdbv2" \
dbsqp/nut-influxdbv2:dev
```

## Debug
To report out further details in the log enable debug:
```
 -e DEBUG="true"
```
