import socket
import binascii
import json

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('0.0.0.0', 33033))

samples =0
t_m = 0.0
p_m = 0.0
h_m = 0.0
j_max = 0

while True:
    data, addr = s.recvfrom(1500)
    print (data, "=>", binascii.hexlify(data))

    j = json.loads(data)
    print (j)

    # This already calculates the averages of the three variables + max size of the message
    samples += 1
    t_m += j[0]
    p_m += j[1]
    h_m += j[2]
    if len(data) > j_max: j_max = len(data)
    print ("{:7.2f} {:10.2f} {:7.2f} | {:}".format(t_m/samples, p_m/samples, h_m/samples, j_max))
