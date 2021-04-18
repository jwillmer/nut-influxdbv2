#!/usr/bin/python
import os
import time
import traceback

from nut2 import PyNUTClient
from influxdb_client import InfluxDBClient, Point, WriteOptions
from influxdb_client.client.write_api import SYNCHRONOUS
import json, socket


# NUT related variables
nut_port = os.getenv('NUT_PORT', '3493')
nut_password = os.getenv('NUT_PASSWORD', 'secret')
nut_username = os.getenv('NUT_USERNAME', 'monuser')
nut_upsname = os.getenv('NUT_UPSNAME', 'ups')
nut_ip_list_str = os.getenv('NUT_IP_LIST', '[]')
nut_host_list_str = os.getenv('NUT_HOST_LIST', '[]')
nut_ip_list=eval(nut_ip_list_str)
nut_host_list=eval(nut_host_list_str)


# Other vars
debug_str = os.getenv('DEBUG', 'false')
remove_keys = ['battery.type','device.serial','ups.realpower.nominal','ups.vendorid','ups.serial','ups.productid','ups.model','ups.mfr','driver.version.data','driver.version','device.type','device.mfr', 'driver.version.internal', 'driver.version.usb', 'ups.beeper.status', 'driver.name', 'battery.mfr.date','ups.firmware', 'ups.firmware.aux','ups.mfr.date', 'battery.date', 'battery.charge.low', 'battery.charge.warning', 'battery.runtime.low','driver.parameter.pollfreq','driver.parameter.pollinterval','driver.parameter.port','input.sensitivity','input.transfer.high','input.transfer.low','ups.delay.shutdown','ups.test.result','ups.timer.reboot','ups.timer.shutdown']

# InfluxDBv2 variables
influxdb2_host=os.getenv('INFLUXDB2_HOST', "localhost")
influxdb2_port=int(os.getenv('INFLUXDB2_PORT', "8086"))
influxdb2_org=os.getenv('INFLUXDB2_ORG', "Home")
influxdb2_token=os.getenv('INFLUXDB2_TOKEN', "token")
influxdb2_bucket=os.getenv('INFLUXDB2_BUCKET', "DEV")

# hard encoded environment variables


# set bebug
if debug_str.lower() == "true":
    debug = True
    nut_debug="true"
else:
    debug = False
    nut_debug=""


# report debug status
if debug:
    print ( " debug: TRUE" )
else:
    print ( " debug: FALSE" )


# get IP address
hostname = socket.gethostname()
host_ip = socket.gethostbyname(hostname)
if debug:
    print ( "docker: "+host_ip )

    
# setup InfluxDB
influxdb2_url="http://" + influxdb2_host + ":" + str(influxdb2_port)
if debug:
    print ( "influx: "+influxdb2_url )
    print ( "bucket: "+influxdb2_bucket )

client = InfluxDBClient(url=influxdb2_url, token=influxdb2_token, org=influxdb2_org)
if client and debug:
    print("influx: online")

write_api = client.write_api(write_options=SYNCHRONOUS)



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
def construct_object(data, remove_keys, host):
    tags = {}
    fields = {}

    tags['source']="NUT"
    tags['host']=host

    for k, v in data.items():
        if k == "ups.serial":
            if v:
                tags["hardware"]=':'.join(v[i:i+2] for i in range(0,12,2))
        elif k == "device.model":
            tags["model"]=v.strip()
        else:
            if k in remove_keys:
                continue
            else:
                fields[k] = convert_to_type(v)

    #watts = float(nut_watts) if nut_watts else float(fields['ups.realpower.nominal'])
    #fields['ups.watts'] = watts * 0.01 * fields['ups.load']

    result ={
            'measurement': 'ups',
            'tags': tags,
            'fields': fields
        }
            
    return result


if debug:
    print("N user: "+nut_username)
    print("N pass: "+nut_password)
    print("IP list:")
    print (json.dumps(nut_ip_list,indent=4))
    print("Host list:")
    print (json.dumps(nut_host_list,indent=4))


# loop over unique names (allows non unique ip for test)
for host in nut_host_list:
    position = nut_host_list.index(host)
    ipaddress = nut_ip_list[position]
    print("\nDO NUT: "+nut_upsname+"@"+ipaddress+" > "+host)

    # setup NUT
    ups_client = PyNUTClient(host=ipaddress, port=nut_port, login=nut_username, password=nut_password, debug=nut_debug) 
    if ups_client and debug:
        print("   NUT: online")

    # push to Influx
    while True:
        try:
            ups_data = ups_client.list_vars(nut_upsname)
            if debug:
                print ("RAW: "+nut_upsname+" @ "+ipaddress)
                print (json.dumps(ups_data,indent=4))
        except:
            tb = traceback.format_exc()
            if debug:
                print(tb)
            print("Error getting data from NUT at "+ipaddress+" "+host)
            exit(1)

    
        json_body = construct_object(ups_data, remove_keys, host)

        try:
            if debug:
                print ("INFLUX: "+influxdb2_bucket+" @ "+host)
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
