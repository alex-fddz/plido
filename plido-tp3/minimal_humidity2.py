from virtual_sensor import virtual_sensor 
import time
import socket
import cbor2 as cbor

humidity = virtual_sensor(start=30, variation = 3, min=20, max=80) 
temperature = virtual_sensor(start=20, variation = 0.1)
pressure    = virtual_sensor(start=1000, variation = 1)
 
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
NB_ELEMENT = 30
h_history = []

while True:

    h = int(humidity.read_value()*100)
    # Gather the other values as well
    t = int(temperature.read_value()*100)
    p = int(pressure.read_value()*100)

    # No more room to store value, send it.
    if len(h_history) == 0:
        # h_history = [h]
        h_history = [[h], [t], [p]]
    elif len(h_history[0]) >= NB_ELEMENT:
        print ("send")
        s.sendto (cbor.dumps(h_history), ("127.0.0.1", 33033))
        # h_history = [h]
        h_history = [[h], [t], [p]]
    else:
        h_history[0].append(h-h_prev) # humidity
        h_history[1].append(t-t_prev) # temperature
        h_history[2].append(p-p_prev) # pressure

    h_prev = h
    t_prev = t
    p_prev = p

    print (len(h_history), len(cbor.dumps(h_history)), h_history)

    time.sleep(10)
