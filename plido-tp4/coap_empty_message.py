import CoAP
import socket

# Server params
SERVER = "192.168.43.82"
PORT = 5683

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

coap = CoAP.Message() # Create a new coap message
coap.new_header()     # A header by default: CONfirmable w code empty (0.00)
coap.dump(hexa=True)

s.settimeout(10)
s.sendto(coap.to_byte(), (SERVER, PORT))

resp, addr = s.recvfrom(2000)
answer = CoAP.Message(resp)
answer.dump(hexa=True)

    
