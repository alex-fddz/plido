# 
# Connect to LoRaWAN network (acklio), get measurements
# from BME280 sensor, encode in CBOR, enclose in CoAP msg,
# and send to acklio server (pokemon sends to Beebotte).
# To use with generic_coap_relay.py & coap_server.py
# (with config_bbt_alex.py) on pokemon server (-tp4).
# -- Last exercise of TP3.1
# 

from network import LoRa
import socket
import time
import pycom
import binascii
import BME280
import kpn_senml.cbor_encoder as cbor
import CoAP
from machine import I2C
from acklio_config import my_app_eui, my_app_key

def CoAP_send_ack_lora(s, coap):
    """Custom CoAP.send_ack method for LoRa/Acklio."""
    import time

    if not coap.get_type() in [CoAP.CON, CoAP.NON]:
        raise ValueError ("Not a CON or NON message")

    c_mid = coap.get_mid()
    timeout = 2
    attempts = 1

    while True:
        s.send(coap.to_byte())

        if coap.get_type() == CoAP.NON:
            return None

        s.settimeout(10)
        try:
            resp,addr = s.recvfrom(2000)
            answer = CoAP.Message(resp)
            if answer.get_mid() == c_mid:
                return answer
        except:
            print ("timeout", timeout, attempts)
            time.sleep (timeout)
            timeout *= 2
            attempts +=1
            if attempts > 4:
                raise ValueError("Too many attempts")

def newCoAPPostMsg(uri_path, payload):
    """
    Create a new CoAP Message of type NON-confirmable,
    with POST code and CBOR-encoded payload.
    """
    msg = CoAP.Message()
    msg.new_header(type=CoAP.NON, code=CoAP.POST)
    msg.add_option(CoAP.Uri_path, uri_path)
    msg.add_option(CoAP.Content_format, 
        CoAP.Content_format_CBOR)
    msg.add_option(CoAP.No_Response, 0x02)
    msg.add_payload(cbor.dumps(payload))
    return msg

def showAnswerIf(answer, s):
    if answer is not None:
        answer.dump()
    else:
        answer = CoAP.get_msg(s)
        if answer is not None:
            answer.dump()

def processData(var_hist, len_hist, new_val, prev_val, uri):
    """
    Build variable's historian and Send when ready.
    Updates len_hist.
    """
    # global NB_ELEMENT 
    # Build variable history array
    if len_hist == 0:
        var_hist = [new_val]
        len_hist = 1
    elif len_hist >= NB_ELEMENT:
        # Build and send CoAP message
        coap_msg = newCoAPPostMsg(uri, var_hist)
        print ("Sending {}...".format(uri), end="\t")
        pycom.rgbled(0x000010) # blue
        try:
            answer = CoAP_send_ack_lora(s, coap_msg)
            showAnswerIf(answer, s)
            print("[OK]")
        except:
            pycom.rgbled(0x100000) # red
            print("[ERR]: Timeout.")
        var_hist = [new_val]
        len_hist = 1
    else:
        var_hist.append(new_val-prev_val)
        len_hist += 1
    return var_hist, len_hist

# -- SETUP --

# Connect to LoRaWAN
lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)

mac = lora.mac()
print ('devEUI: ', binascii.hexlify(mac))

# create an OTAA authentication parameters
app_eui = binascii.unhexlify(
    my_app_eui.replace(' ',''))

app_key = binascii.unhexlify(
    my_app_key.replace(' ',''))

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
s.setsockopt(socket.SOL_LORA, socket.SO_CONFIRMED, False)

# Connect BME280 sensor
i2c = I2C(0, I2C.MASTER, baudrate=400000)
print (i2c.scan())

bme = BME280.BME280(i2c=i2c)

# -- MAIN --

# Set params
MEAS_INTERVAL = 10 # secs
SEND_INTERVAL = 1 # mins
NB_ELEMENT = int(SEND_INTERVAL * 60 / MEAS_INTERVAL)
print("- Measuring every", MEAS_INTERVAL, 
    "seconds, and sending every", SEND_INTERVAL,
    "minute(s):", NB_ELEMENT, "elements per message.")

t_history, t_prev = [], 0
h_history, h_prev = [], 0
p_history, p_prev = [], 0
# For some reason I cannot use len() !?!?
len_t = 0
len_h = 0
len_p = 0

# Extra/challenge: Also send available memory
m_history, m_prev = [], 0
len_m = 0

while True:
    # Config socket/send msg
    s.setblocking(True)
    s.settimeout(10)

    # Flash green while obtaining measurements
    pycom.rgbled(0x001000)
    
    t = int(bme.read_temperature()*100)
    h = int(bme.read_humidity()*100)
    p = int(bme.read_pressure()*100)
    
    free, total = pycom.get_free_heap()
    m = int(100 * free / total)

    # Build historians and send when ready
    t_history, len_t = processData(t_history, len_t, 
        t, t_prev, "temperature")
    h_history, len_h = processData(h_history, len_h, 
        h, h_prev, "humidity")
    p_history, len_p = processData(p_history, len_p, 
        p, p_prev, "pressure")
    m_history, len_m = processData(m_history, len_m, 
        m, m_prev, "memory")

    t_prev = t
    h_prev = h
    p_prev = p
    m_prev = m

    # Turn off led while sleeping
    pycom.rgbled(0x000000)
    print("(", len_t, "/", NB_ELEMENT, ")", 
        " z Z z z")
    s.setblocking(False)
    time.sleep(MEAS_INTERVAL)
