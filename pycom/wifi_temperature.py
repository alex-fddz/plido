import BME280
import time
import socket
import kpn_senml.cbor_encoder as cbor
from machine import I2C

server_ip = "192.168.43.82"
server_port = 33033

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
NB_ELEMENT = 30
t_history = []
h_history = []
p_history = []

i2c = I2C(0, I2C.MASTER, baudrate=400000)
print (i2c.scan())

bme = BME280.BME280(i2c=i2c)

while True:

    t = int(bme.read_temperature()*100)
    h = int(bme.read_humidity()*100)
    p = int(bme.read_pressure()*100)

    # Build Temperature historian msg
    if len(t_history) == 0:
        t_history = [t]
    elif len(t_history) >= NB_ELEMENT:
        print ("Sending temperature...")
        s.sendto (cbor.dumps(["temperature", t_history]), (server_ip, server_port))
        t_history = [t]
    else:
        t_history.append(t-t_prev)

    # Build Humidity historian msg
    if len(h_history) == 0:
        h_history = [h]
    elif len(h_history) >= NB_ELEMENT:
        print ("Sending humidity...")
        s.sendto (cbor.dumps(["humidity", h_history]), (server_ip, server_port))
        h_history = [h]
    else:
        h_history.append(h-h_prev)

    # Build Pressure historian msg
    if len(p_history) == 0:
        p_history = [p]
    elif len(p_history) >= NB_ELEMENT:
        print ("Sending pressure...")
        s.sendto (cbor.dumps(["pressure", p_history]), (server_ip, server_port))
        p_history = [p]
    else:
        p_history.append(p-p_prev)

    t_prev = t
    h_prev = h
    p_prev = p

    # Print size
    print (len(t_history), len(cbor.dumps(t_history)), t_history)

    time.sleep(10)
