import CoAP
import socket

# Server params
SERVER = "192.168.43.82"
PORT = 5683

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Create a new coap message
coap = CoAP.Message() 
# Create a header with code GET (000,00001) = 0x01
coap.new_header(code=CoAP.GET)
# Add option: uri path (11--) with value 'time' (size 00,0100) = 0xb4
coap.add_option(CoAP.Uri_path, "time")

# Print out the message we're about to send
print("[SND]:", end=" ")
coap.dump(hexa=True)

# Send the message
s.settimeout(10)
s.sendto(coap.to_byte(), (SERVER, PORT))

# I. Await for a response/answer from the server (receiver)
resp, addr = s.recvfrom(2000)
answer = CoAP.Message(resp) # 'parse' it as a coap message
# Print out the message we just got (ACK)
print("[RCV]:", end=" ")
answer.dump(hexa=True)

# II. Now we must also get the message with the actual content
resp, addr = s.recvfrom(2000)
answer = CoAP.Message(resp) # 'parse' it as a coap message
# Print out the message we just got
print("[RCV]:", end=" ")
answer.dump(hexa=True)

