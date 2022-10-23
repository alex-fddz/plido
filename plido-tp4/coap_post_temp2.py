# Send a POST coap msg w uri path = /temp, a value of 23.5 encoded in CBOR, 
# await an answer (ACK) w the response.
# - Use with coap_basic_server3.py

import CoAP
import socket
import time
try: # pycom
    import kpn_senml.cbor_encoder as cbor
except: # terminal on computer
    import cbor2 as cbor

# Server params
SERVER = "192.168.43.82"
PORT = 5683
destination = (SERVER, PORT)

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Create a new coap message
msg = CoAP.Message() 
# Create a header with code POST (000,00002) = 0x02
msg.new_header(code=CoAP.POST)
# Add option: uri path (11--) with value 'time' (size 00,0100) = 0xb4
msg.add_option(CoAP.Uri_path, "temp")
# Encode the "23.5" value in cbor
msg.add_option(CoAP.Content_format, CoAP.Content_format_CBOR)
msg.add_payload( cbor.dumps(23.5) )

# Print out the message we're about to send
print("[SND]:", end=" ")
msg.dump(hexa=True)

# Send the message and expect an ACK 
answer = CoAP.send_ack(s, destination, msg)
# Print out the message we just got
print("[RCV]:", end=" ")
answer.dump(hexa=True)
