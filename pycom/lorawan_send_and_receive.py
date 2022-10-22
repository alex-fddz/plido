from network import LoRa
import socket
import time
import pycom
import binascii

# pycom params
my_app_eui = '0000000000000000'
my_app_key = '72457475581217131977635496807027'

lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)
#
mac = lora.mac()
print ('devEUI: ',  binascii.hexlify(mac))

# create an OTAA authentication parameters
app_eui = binascii.unhexlify(
    my_app_eui.replace(' ',''))

app_key = binascii.unhexlify(
    my_app_key.replace(' ',''))
    #'B0923EE49E056F29C1482EE5846FADF4'.replace(' ',''))  # TTN
    #'11223344556677881122334455667788'.replace(' ',''))  # Acklio
    #'11 00 22 00 33 00 44 00 55 00 66 00 77 00 88 00'.replace(' ',''))  # chirpstack

pycom.heartbeat(False)
pycom.rgbled(0x101010) # white
print("> Joining LoRa...")

# join a network using OTAA (Over the Air Activation)
lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key), 
    timeout=0)

# wait until the module has joined the network
while not lora.has_joined():
    time.sleep(2.5)
    print('Not yet joined...')

print("> Joined LoRa.")
pycom.rgbled(0x000000) # black

# Passer les params a la couche protocolaire LoRa
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)
s.setsockopt(socket.SOL_LORA,  socket.SO_CONFIRMED,  False)

while True:
    pycom.rgbled(0x100000) # red
    s.setblocking(True)
    s.settimeout(10)

    print("> Sending msg...")
    try:
        s.send('Hello LoRa')
        print("  > Msg sent!")
    except:
        print ('  timeout in sending')

    pycom.rgbled(0x000010) # blue
    print("> Awaiting msg...")

    try:
        data = s.recv(64)

        print(data)
        pycom.rgbled(0x001000) # green
        print("  > Msg received!")
    except:
        print ('  timeout in receive')
        pycom.rgbled(0x000000) # black

    print(" z Z z z")
    s.setblocking(False)
    time.sleep (29)
