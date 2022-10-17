import socket
import binascii

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('0.0.0.0', 33033))

total = 0
n = 0

while True:
    data, addr = s.recvfrom(1500)
    print (data, "=>", binascii.hexlify(data))

    # print("The number is", float(data))
    n += 1
    total += float(data)
    avg = total / n
    print("Average so far =", avg)
