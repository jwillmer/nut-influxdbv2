#!/usr/bin/python
import os
import time
import traceback

from nut2 import PyNUTClient
#from influxdb import InfluxDBClient

from influxdb_client import InfluxDBClient, Point, WriteOptions
from influxdb_client.client.write_api import SYNCHRONOUS
import json



# InfluxDB details
dbname = os.getenv('INFLUXDB_DATABASE', 'nutupstest')
username = os.getenv('INFLUXDB_USER')
password = os.getenv('INFLUXDB_PASSWORD')
host = os.getenv('INFLUXDB_HOST', '127.0.0.1')
port = os.getenv('INFLUXDB_PORT', 8086)
# NUT related variables
nut_host = os.getenv('NUT_HOST', '127.0.0.1')
nut_port = os.getenv('NUT_PORT') if os.getenv('NUT_PORT') != '' else '3493'
nut_password = os.getenv('NUT_PASSWORD') if os.getenv('NUT_PASSWORD') != '' else None
nut_username = os.getenv('NUT_USERNAME') if os.getenv('NUT_USERNAME') != '' else None
nut_watts = os.getenv('WATTS') if os.getenv('WATTS') != '' else None
# Other vars
interval = float(os.getenv('INTERVAL', 21))
ups_name = os.getenv('UPS_NAME', 'UPS')
verbose = os.getenv('VERBOSE', 'false').lower()
remove_keys = ['battery.type','device.serial','ups.realpower.nominal','ups.vendorid','ups.serial','ups.productid','ups.model','ups.mfr','driver.version.data','driver.version','device.type','device.mfr', 'driver.version.internal', 'driver.version.usb', 'ups.beeper.status', 'driver.name', 'battery.mfr.date','ups.firmware', 'ups.firmware.aux','ups.mfr.date', 'battery.date', 'battery.charge.low', 'battery.charge.warning', 'battery.runtime.low','driver.parameter.pollfreq','driver.parameter.pollinterval','driver.parameter.port','input.sensitivity','input.transfer.high','input.transfer.low','ups.delay.shutdown','ups.test.result','ups.timer.reboot','ups.timer.shutdown']

# InfluxDBv2 variables
influxdb2_host=os.getenv('INFLUXDB2_HOST', "localhost")
influxdb2_port=int(os.getenv('INFLUXDB2_PORT', "8086"))
influxdb2_org=os.getenv('INFLUXDB2_ORG', "org")
influxdb2_token=os.getenv('INFLUXDB2_TOKEN', "token")
influxdb2_bucket=os.getenv('INFLUXDB2_BUCKET', "netatmo")

# hard encoded environment variables
nut_host = "10.0.0.10"
nut_port = "3493"
nut_password = "secret"
nut_username = "monuser"
nut_watts = "200"
interval = 5
counter = 1
nut_hostname = "NAS"
ups_name = "ups"
nut_debug =False
verbose = "true"
influxdb2_host="10.0.0.10"
influxdb2_port="8086"
influxdb2_org="Home"
influxdb2_token="SbfFAjZxi1v2mYno0VvVPkXXXJju8LRQ99MJ77l73FfgIMaSxuK_nVG1wpPcnMF7KAnZ4c-dMqpkSTr4F2I78w=="
influxdb2_bucket="DEV"

print("Connecting to InfluxDBv2 host:{}, org:{}, bucket:{}".format(influxdb2_host, influxdb2_org, influxdb2_bucket))
influxdb2_url="http://" + influxdb2_host + ":" + str(influxdb2_port)
client = InfluxDBClient(url=influxdb2_url, token=influxdb2_token, org=influxdb2_org)
write_api = client.write_api(write_options=SYNCHRONOUS)

if client:
    print("Connected successfully to InfluxDBv2")

if verbose:
    #print("INFLUXDB_DATABASE: ", dbname)
    #print("INFLUXDB_USER: ", username)
    # print("INFLUXDB_PASSWORD: ", password)    # Not really safe to just print it. Feel free to uncomment this if you really need it
    #print("INFLUXDB_PORT: ", port)
    #print("INFLUXDB_HOST: ", host)

    print("  INFLUXDB2_HOST: ", influxdb2_host)
    print("  INFLUXDB2_PORT: ", influxdb2_port)
    print("   INFLUXDB2_ORG: ", influxdb2_org)
    print(" INFLUXDB2_TOKEN: ", influxdb2_token) # Not really safe to just print it. Feel free to uncomment this if you really need it
    print("INFLUXDB2_BUCKET: ", influxdb2_bucket)

    print("NUT_USER: ", nut_username)
    print("NUT_PASS: ", nut_password)
    print("UPS_NAME: ", ups_name)
    print("INTERVAL: ", interval)
    print(" VERBOSE: ", verbose)

print("Connecting to NUT host {}:{}".format(nut_host, nut_port))
ups_client = PyNUTClient(host=nut_host, port=nut_port, login=nut_username, password=nut_password, debug=nut_debug)
if ups_client:
    print("Connected successfully to NUT")


def convert_to_type(s):
    """ A function to convert a str to either integer or float. If neither, it will return the str. """
    try:
        int_var = int(s)
        return int_var
    except ValueError:
        try:
            float_var = float(s)
            return float_var
        except ValueError:
            return s


def construct_object(data, remove_keys):
    tags = {}
    fields = {}

    tags['source']="NUT"
    tags['host']=nut_hostname

    for k, v in data.items():
        if k == "device.model":
            tags["module"]=v
        else:
            if k in remove_keys:
                continue
            else:
                fields[k] = convert_to_type(v)

    watts = float(nut_watts) if nut_watts else float(fields['ups.realpower.nominal'])
    fields['ups.power'] = watts * 0.01 * fields['ups.load']

    result ={
            'measurement': 'ups',
            'tags': tags,
            'fields': fields
        }
            
    return result


# Main infinite loop: Get the data from NUT every interval and send it to InfluxDB.
while True:
    try:
        ups_data = ups_client.list_vars(ups_name)
    except:
        tb = traceback.format_exc()
        if verbose == 'true':
            print(tb)
        print("Error getting data from NUT")
        exit(1)

    json_body = construct_object(ups_data, remove_keys)

    try:
        if verbose == 'true':
            print ("\n#: "+str(counter))
            print ("INFLUX: "+influxdb2_bucket)
            print (json.dumps(json_body,indent=4))
        write_api.write(bucket=influxdb2_bucket, org=influxdb2_org, record=[json_body])

    except:
        tb = traceback.format_exc()
        if verbose == 'true':
            print(tb)
        print("Error connecting to InfluxDB.")
        exit(2)

    counter = counter + 1
    time.sleep( interval )
