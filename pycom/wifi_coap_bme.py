# 
# Connect to WIFI, get measurements from BME280 sensor, 
# encode in CBOR, enclose in CoAP msg, send to laptop.
# To use with coap_server.py (sends to bbt)
# -- Last exercise of TP3.1 (+ lorawan version)
# 

import socket
import time
import pycom
import binascii
import BME280
import kpn_senml.cbor_encoder as cbor
import CoAP
from machine import I2C

def newCoAPPostMsg(uri_path, payload):
    """
    Create a new CoAP Message of type NON-confirmable,
    with POST code and CBOR-encoded payload.
    """
    msg = CoAP.Message()
    msg.new_header(type=CoAP.NON, code=CoAP.POST)
    msg.add_option(CoAP.Uri_path, uri_path)
    msg.add_option(CoAP.Content_format, 
        CoAP.Content_format_CBOR)
    msg.add_option(CoAP.No_Response, 0x02)
    msg.add_payload(cbor.dumps(payload))
    return msg

def showAnswerIf(answer, s):
    if answer is not None:
        answer.dump()
    else:
        answer = CoAP.get_msg(s)
        if answer is not None:
            answer.dump()


server_ip = "192.168.43.82"
server_port = 5683
destination = (server_ip, server_port)

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# -- MAIN --

# Connect BME280 sensor
i2c = I2C(0, I2C.MASTER, baudrate=400000)
print (i2c.scan())

bme = BME280.BME280(i2c=i2c)

# Set params
MEAS_INTERVAL = 10 # secs
SEND_INTERVAL = 1 # mins
NB_ELEMENT = int(SEND_INTERVAL * 60 / MEAS_INTERVAL)
print("- Measuring every", MEAS_INTERVAL, 
    "seconds, and sending every", SEND_INTERVAL,
    "minute(s):", NB_ELEMENT, "elements per message.")

t_history = []
h_history = []
p_history = []
# For some reason I cannot use len() !?!?
len_t = 0
len_h = 0
len_p = 0

while True:
    # Config socket/send msg
    s.setblocking(True)
    s.settimeout(10)

    # Flash green while obtaining measurements
    #pycom.rgbled(0x001000)
    
    t = int(bme.read_temperature()*100)
    h = int(bme.read_humidity()*100)
    p = int(bme.read_pressure()*100)
    
    # Build Temperature historian msg
    if len_t == 0:
        t_history = [t]
        len_t = 1
    elif len_t >= NB_ELEMENT:
        # Build CoAP message
        t_coap = newCoAPPostMsg("temperature", t_history)
        print ("Sending temperature...", end="\t")
        #pycom.rgbled(0x000010) # blue
        try:
            answer = CoAP.send_ack(s, destination, t_coap)
            showAnswerIf(answer, s)
            print("[OK]")
        except:
            #pycom.rgbled(0x100000) # red
            print("[ERR]: Timeout.")
        t_history = [t]
        len_t = 1
    else:
        t_history.append(t-t_prev)
        len_t += 1

    # Build Humidity historian msg
    if len_h == 0:
        h_history = [h]
        len_h = 1
    elif len_h >= NB_ELEMENT:
        # Build CoAP message
        h_coap = newCoAPPostMsg("humidity", h_history)
        print ("Sending humidity...", end="\t")
        #pycom.rgbled(0x000010) # blue
        try:
            answer = CoAP.send_ack(s, destination, h_coap)
            showAnswerIf(answer, s)
            print("[OK]")
        except:
            #pycom.rgbled(0x100000) # red
            print("[ERR]: Timeout.")
        h_history = [h]
        len_h = 1
    else:
        h_history.append(h-h_prev)
        len_h += 1

    # Build Pressure historian msg
    if len_p == 0:
        p_history = [p]
        len_p = 1
    elif len_p >= NB_ELEMENT:
        # Build CoAP message
        p_coap = newCoAPPostMsg("pressure", p_history)
        print("Sending pressure...", end="\t")
        #pycom.rgbled(0x000010) # blue
        try:
            answer = CoAP.send_ack(s, destination, p_coap)
            showAnswerIf(answer, s)
            print("[OK]")
        except:
            #pycom.rgbled(0x100000) # red
            print("[ERR]: Timeout.")
        p_history = [p]
        len_p = 1
    else:
        p_history.append(p-p_prev)
        len_p += 1

    t_prev = t
    h_prev = h
    p_prev = p

    # Turn off led while sleeping
    #pycom.rgbled(0x000000)
    print("(", len_t, "/", NB_ELEMENT, ")", 
        " z Z z z")
    s.setblocking(False)
    time.sleep(MEAS_INTERVAL)
