# nut-influxdbv2

This is a docker container that pulls data from a NUT server and pushed to InfluxDB. Based on work of mihai-cindea [https://github.com/mihai-cindea/nut-influxdb-exporter)

## Changes
Updated for InfluxDBv2. Changed outputted values.

## Roadmap
Add poll of multiple NUT servers by env varable of server IP addresses

## How to run
```
$ docker run -d \
 -e NUT_HOST="<NUT Server IP address>" \
 -e NUT_PORT="<NUT Port>" \
 -e NUT_PASSWORD="<NUT password>" \
 -e NUT_USERNAME="<NUT username>" \
 -e NUT_HOSTNAME="<Influx Host Tag>" \
 -e NUT_UPSNAME="<NUT UPS Name>" \
 -e INFLUXDB2_HOST="<INFLUXDBv2 SERVER>" \
 -e INFLUXDB2_PORT="8086" \
 -e INFLUXDB2_ORG="" \
 -e INFLUXDB2_TOKEN="" \
 -e INFLUXDB2_BUCKET="" \
 --name "nut-influxdbv2" \
dbsqp/nut-influxdbv2:latest
```

## Debug
To report out further details in the log enable debug:
```
 -e DEBUG="true"
```
