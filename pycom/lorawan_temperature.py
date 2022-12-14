# 
# Connect to LoRaWAN network (acklio), get measurements
# from BME280 sensor and send them to beebotte.
# To use with generic_relay.py & display_server_alex.py
# (with config_bbt_alex.py) on pokemon server.
# -- Last exercise of TP2.3
# 

from network import LoRa
import socket
import time
import pycom
import binascii
import BME280
import kpn_senml.cbor_encoder as cbor
from machine import I2C
from acklio_config import my_app_eui, my_app_key

lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)

mac = lora.mac()
print ('devEUI: ', binascii.hexlify(mac))

# create an OTAA authentication parameters
app_eui = binascii.unhexlify(
    my_app_eui.replace(' ',''))

app_key = binascii.unhexlify(
    my_app_key.replace(' ',''))

pycom.heartbeat(False)
pycom.rgbled(0x101010) # white
print("> Joining LoRa...")

# join a network using OTAA (Over the Air Activation)
lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key), 
    timeout=0)

# wait until the module has joined the network
while not lora.has_joined():
    time.sleep(2.5)
    print('Not yet joined...')

print("> Joined LoRa.")
pycom.rgbled(0x000000) # black

# Passer les params a la couche protocolaire LoRa
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)
s.setsockopt(socket.SOL_LORA,  socket.SO_CONFIRMED,  False)

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
    pycom.rgbled(0x001000)
    
    t = int(bme.read_temperature()*100)
    h = int(bme.read_humidity()*100)
    p = int(bme.read_pressure()*100)
    
    # Build Temperature historian msg
    if len_t == 0:
        t_history = [t]
        len_t = 1
    elif len_t >= NB_ELEMENT:
        print ("Sending temperature...", end="\t")
        pycom.rgbled(0x000010) # blue
        try:
            s.send( cbor.dumps(["temperature", t_history]) )
            print("[OK]")
        except:
            pycom.rgbled(0x100000) # red
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
        print ("Sending humidity...", end="\t")
        pycom.rgbled(0x000010) # blue
        try:
            s.send( cbor.dumps(["humidity", h_history]) )
            print("[OK]")
        except:
            pycom.rgbled(0x100000) # red
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
        print("Sending pressure...", end="\t")
        pycom.rgbled(0x000010) # blue
        try:
            s.send( cbor.dumps(["pressure", p_history]) )
            print("[OK]")
        except:
            pycom.rgbled(0x100000) # red
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
    pycom.rgbled(0x000000)
    print("(", len_t, "/", NB_ELEMENT, ")", 
        " z Z z z")
    s.setblocking(False)
    time.sleep(MEAS_INTERVAL)
