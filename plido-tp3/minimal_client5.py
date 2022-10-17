from virtual_sensor import virtual_sensor 
import time
import socket
import cbor2 as cbor

temperature = virtual_sensor(start=20, variation = 0.1)
pressure    = virtual_sensor(start=1000, variation = 1) 
humidity    = virtual_sensor(start=30, variation = 3, min=20, max=80) 
 
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    t = int(temperature.read_value()) # max is 4000
    p = int(pressure.read_value()) # max is 1000
    h = int(humidity.read_value()) # max is 10000

    j = [t, p, h]
    s.sendto (cbor.dumps(j), ("127.0.0.1", 33033))
    time.sleep(10)
