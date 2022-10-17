import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.sendto("hello world", ("192.168.43.82", 33033))
