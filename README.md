# nut-influxdbv2

This is a docker container that pulls data from a set of NUT servers and pushed to InfluxDB. Based on work of jankeesvw [evohome-to-influxdb] (https://github.com/jankeesvw/evohome-to-influxdb)

Updated for InfluxDBv2. Changed output

Add multi server in future

How to run

$ docker run -d \
 -e EVOHOME_APP_ID="<evohome API application id>" \
 -e EVOHOME_USERNAME="<evohome email>" \
 -e EVOHOME_PASSWORD="<evohome password>" \
 -e INFLUXDB2_HOST="<INFLUXDBv2 SERVER>" \
 -e INFLUXDB2_PORT="8086" \
 -e INFLUXDB2_ORG="" \
 -e INFLUXDB2_TOKEN="" \
 -e INFLUXDB2_BUCKET="" \
 --name "nut-influxdbv2" \
dbsqp/nut-influxdbv2:latest
