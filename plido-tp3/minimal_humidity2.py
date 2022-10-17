from virtual_sensor import virtual_sensor 
import time
import socket
import cbor2 as cbor

humidity    = virtual_sensor(start=30, variation = 3, min=20, max=80) 
temperature = virtual_sensor(start=20, variation = 0.1)
pressure    = virtual_sensor(start=1000, variation = 1)
 
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
NB_ELEMENT = 30
h_history = []
t_history = []
p_history = []

while True:

    h = int(humidity.read_value()*100)
    # Gather the other values as well
    t = int(temperature.read_value()*100)
    p = int(pressure.read_value()*100)

    # Build humidity historian msg
    if len(h_history) == 0:
        h_history = [h]
    elif len(h_history) >= NB_ELEMENT:
        print ("Sending humidity...")
        s.sendto (cbor.dumps(["humidity", h_history]), ("127.0.0.1", 33033))
        h_history = [h]
    else:
        h_history.append(h-h_prev)

    # Build temperature historian msg
    if len(t_history) == 0:
        t_history = [t]
    elif len(t_history) >= NB_ELEMENT:
        print ("Sending temperature...")
        s.sendto (cbor.dumps(["temperature", t_history]), ("127.0.0.1", 33033))
        t_history = [t]
    else:
        t_history.append(t-t_prev)

    # Build pressure historian msg
    if len(p_history) == 0:
        p_history = [p]
    elif len(p_history) >= NB_ELEMENT:
        print ("Sending pressure...")
        s.sendto (cbor.dumps(["pressure", p_history]), ("127.0.0.1", 33033))
        p_history = [p]
    else:
        p_history.append(p-p_prev)

    h_prev = h
    t_prev = t
    p_prev = p

    # Print size
    print (len(h_history), len(cbor.dumps(h_history)), h_history)

    time.sleep(10)
