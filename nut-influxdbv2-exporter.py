#!/usr/bin/python
import os
import time
import traceback

from datetime import datetime
from nut2 import PyNUTClient
from influxdb_client import InfluxDBClient, Point, WriteOptions
from influxdb_client.client.write_api import SYNCHRONOUS
import json, socket

# InfluxDB details
influxdb2_host = os.getenv("INFLUXDB2_HOST", "localhost")
influxdb2_port = int(os.getenv("INFLUXDB2_PORT", "8086"))
influxdb2_org = os.getenv("INFLUXDB2_ORG", "Home")
influxdb2_token = (
    os.getenv("INFLUXDB2_TOKEN") if os.getenv("INFLUXDB2_TOKEN") != "" else None
)
influxdb2_bucket = os.getenv("INFLUXDB2_BUCKET", "DEV")
influxdb2_ssl = os.getenv("INFLUXDB2_SSL", "False").lower() == "true"
influxdb2_ssl_verify = os.getenv("INFLUXDB2_SSL_VERIFY", "False").lower() == "true"
influxdb2_measurement = os.getenv("INFLUXDB2_MEASUREMENT", "ups_status")

# NUT related variables
nut_host = os.getenv("NUT_HOST", "127.0.0.1")
nut_port = os.getenv("NUT_PORT") if os.getenv("NUT_PORT") != "" else "3493"
nut_password = os.getenv("NUT_PASSWORD") if os.getenv("NUT_PASSWORD") != "" else None
nut_username = os.getenv("NUT_USERNAME") if os.getenv("NUT_USERNAME") != "" else None
nut_watts = os.getenv("WATTS") if os.getenv("WATTS") != "" else None

# Other vars
interval = float(os.getenv("INTERVAL", 21))
ups_name = os.getenv("UPS_NAME", "UPS")
verbose = os.getenv("VERBOSE", "false").lower()
remove_keys = [
    "driver.version.internal",
    "driver.version.usb",
    "ups.beeper.status",
    "driver.name",
    "battery.mfr.date",
]
tag_keys = [
    "battery.type",
    "device.model",
    "device.serial",
    "driver.version",
    "driver.version.data",
    "device.mfr",
    "device.type",
    "ups.mfr",
    "ups.model",
    "ups.productid",
    "ups.serial",
    "ups.vendorid",
]


def convert_to_type(s):
    """A function to convert a str to either integer or float. If neither, it will return the str."""
    try:
        int_var = int(s)
        return int_var
    except ValueError:
        try:
            float_var = float(s)
            return float_var
        except ValueError:
            return s


def construct_object(data, remove_keys, tag_keys):
    """
    Constructs NUT data into  an object that can be sent directly to InfluxDB

    :param data: data received from NUT
    :param remove_keys: some keys which are considered superfluous
    :param tag_keys: some keys that are actually considered tags and not measurements
    :return:
    """
    fields = {}
    tags = {"host": os.getenv("HOSTNAME", "localhost")}

    for k, v in data.items():
        if k not in remove_keys:
            if k in tag_keys:
                tags[k] = v
            else:
                fields[k] = convert_to_type(v)

    watts = float(nut_watts) if nut_watts else float(fields["ups.realpower.nominal"])
    fields["watts"] = watts * 0.01 * fields["ups.load"]

    result = [{"measurement": influxdb2_measurement, "fields": fields, "tags": tags}]
    return result


if influxdb2_ssl:
    influxdb2_url = "https://" + influxdb2_host + ":" + str(influxdb2_port)
else:
    influxdb2_url = "http://" + influxdb2_host + ":" + str(influxdb2_port)

if verbose == "true":
    print("INFLUXDB_HOST: ", influxdb2_host)
    print("INFLUXDB_PORT: ", influxdb2_port)
    print("INFLUXDB2_TOKEN set: ", influxdb2_token is not None)
    print("INFLUXDB_BUCKET: ", influxdb2_bucket)
    print("INFLUXDB_ORG: ", influxdb2_org)
    print("INFLUXDB2_SSL_VERIFY: ", influxdb2_ssl_verify)
    print()

print("Connecting to URL: " + influxdb2_url + " verify_ssl=", influxdb2_ssl_verify)
client = InfluxDBClient(
    url=influxdb2_url,
    token=influxdb2_token,
    org=influxdb2_org,
    verify_ssl=(influxdb2_ssl_verify),
)

if client:
    print("Connected successfully to InfluxDB")
else:
    print("InfluxDB connection failed!")

write_api = client.write_api(write_options=SYNCHRONOUS)


if verbose == "true":
    print()
    print("NUT_HOST: ", nut_host)
    print("NUT_USER: ", nut_username)
    print("NUT_PASSWORD set: ", nut_password is not None)
    print("NUT_PORT: ", nut_port)
    print("UPS_NAME", ups_name)
    print("WATTS", nut_watts)
    print("Loop INTERVAL: ", interval)
    print()

print("Connecting to NUT host {}:{}".format(nut_host, nut_port))

ups_client = PyNUTClient(
    host=nut_host,
    port=nut_port,
    login=nut_username,
    password=nut_password,
    debug=(verbose == "true"),
)
if ups_client:
    print("Connected successfully to NUT")

# Main infinite loop: Get the data from NUT every interval and send it to InfluxDB.
while True:
    if verbose == "true":
        now = datetime.now()
        print("Loop execution time: ", now)

    try:
        ups_data = ups_client.list_vars(ups_name)
    except:
        tb = traceback.format_exc()
        if verbose == "true":
            print(tb)
        print("Error getting data from NUT")
        exit(1)

    json_body = construct_object(ups_data, remove_keys, tag_keys)

    try:
        if verbose == "true":
            print("INFLUX: " + influxdb2_bucket + " @ " + influxdb2_host)
            print(json.dumps(json_body, indent=4))

        write_api.write(bucket=influxdb2_bucket, org=influxdb2_org, record=[json_body])
    except:
        tb = traceback.format_exc()
        if verbose == "true":
            print(tb)
        print("Error connecting to InfluxDB.")
        exit(2)

    time.sleep(interval)
