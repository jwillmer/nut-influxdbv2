#!/usr/bin/python
import os
import time
import traceback

from nut2 import PyNUTClient
from influxdb_client import InfluxDBClient, Point, WriteOptions
from influxdb_client.client.write_api import SYNCHRONOUS
import json



# InfluxDB details
host = os.getenv('INFLUXDB_HOST', '127.0.0.1')
port = os.getenv('INFLUXDB_PORT', 8086)

# NUT related variables
nut_host = os.getenv('NUT_HOST', '127.0.0.1')
nut_port = os.getenv('NUT_PORT', '3493')
nut_password = os.getenv('NUT_PASSWORD', 'secret')
nut_username = os.getenv('NUT_USERNAME', 'monuser')
nut_hostname = os.getenv('NUT_HOSTNAME', 'localhost')
nut_upsname = os.getenv('NUT_UPSNAME', 'ups')

# Other vars
debug_str = os.getenv('DEBUG', 'false')
remove_keys = ['battery.type','device.serial','ups.realpower.nominal','ups.vendorid','ups.serial','ups.productid','ups.model','ups.mfr','driver.version.data','driver.version','device.type','device.mfr', 'driver.version.internal', 'driver.version.usb', 'ups.beeper.status', 'driver.name', 'battery.mfr.date','ups.firmware', 'ups.firmware.aux','ups.mfr.date', 'battery.date', 'battery.charge.low', 'battery.charge.warning', 'battery.runtime.low','driver.parameter.pollfreq','driver.parameter.pollinterval','driver.parameter.port','input.sensitivity','input.transfer.high','input.transfer.low','ups.delay.shutdown','ups.test.result','ups.timer.reboot','ups.timer.shutdown']

# InfluxDBv2 variables
influxdb2_host=os.getenv('INFLUXDB2_HOST', "localhost")
influxdb2_port=int(os.getenv('INFLUXDB2_PORT', "8086"))
influxdb2_org=os.getenv('INFLUXDB2_ORG', "org")
influxdb2_token=os.getenv('INFLUXDB2_TOKEN', "token")
influxdb2_bucket=os.getenv('INFLUXDB2_BUCKET', "DEV")

# hard encoded environment variables


# set bebug
if debug_str.lower() == "true":
    debug = True
    nut_debug="true"
else:
    debug = False
    nut_debug="false"


# report debug status
if debug:
    print ( " debug: TRUE" )
else:
    print ( " debug: FALSE" )


# setup InfluxDB
influxdb2_url="http://" + influxdb2_host + ":" + str(influxdb2_port)
if debug:
    print ( "influx: "+influxdb2_url )
    print ( "bucket: "+influxdb2_bucket )

client = InfluxDBClient(url=influxdb2_url, token=influxdb2_token, org=influxdb2_org)
if client and debug:
    print("Influx: OK")

write_api = client.write_api(write_options=SYNCHRONOUS)


# setup NUT
if debug:
    print("NUT_USER: ", nut_username)
    print("NUT_PASS: ", nut_password)
ups_client = PyNUTClient(host=nut_host, port=nut_port, login=nut_username, password=nut_password, debug=nut_debug) 
if ups_client and debug:
    print("NUT: OK")

# define convert
def convert_to_type(s):
    try:
        int_var = int(s)
        return int_var
    except ValueError:
        try:
            float_var = float(s)
            return float_var
        except ValueError:
            return s

#define data object
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

    #watts = float(nut_watts) if nut_watts else float(fields['ups.realpower.nominal'])
    #fields['ups.power'] = watts * 0.01 * fields['ups.load']

    result ={
            'measurement': 'ups',
            'tags': tags,
            'fields': fields
        }
            
    return result


# Main
while True:
    try:
        ups_data = ups_client.list_vars(nut_upsname)
        if debug:
            print ("UPS: "+nut_upsname)
            print (json.dumps(ups_data,indent=4))
    except:
        tb = traceback.format_exc()
        if debug:
            print(tb)
        print("Error getting data from NUT")
        exit(1)
    
    json_body = construct_object(ups_data, remove_keys)

    try:
        if debug:
            print ("INFLUX: "+influxdb2_bucket)
            print (json.dumps(json_body,indent=4))
        write_api.write(bucket=influxdb2_bucket, org=influxdb2_org, record=[json_body])
        break
    except:
        tb = traceback.format_exc()
        if debug:
            print(tb)
        print("Error connecting to InfluxDBv2")
        exit(2)

    time.sleep( 5 )

