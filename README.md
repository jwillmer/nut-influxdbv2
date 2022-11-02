# nut-influxdbv2
Docker image to pulls data from a NUT server and push it to an InfluxDB bucket. Based on work of [mihai-cindea](https://github.com/mihai-cindea/nut-influxdb-exporter) and [dbsqp](https://github.com/dbsqp/nut-influxdbv2).

## Environment variables with default values
```
# InfluxDB details
INFLUXDB2_HOST: localhost
INFLUXDB2_PORT: 8086
INFLUXDB2_ORG: Home
INFLUXDB2_TOKEN: ''
INFLUXDB2_BUCKET: DEV
INFLUXDB2_SSL: false
INFLUXDB2_SSL_VERIFY: false

# NUT related variables
NUT_HOST: 127.0.0.1
NUT_PORT: 3493
NUT_PASSWORD: ''
NUT_USERNAME: ''
WATTS: ''

# Other vars
INTERVAL: 21
UPS_NAME: UPS
VERBOSE: false
```