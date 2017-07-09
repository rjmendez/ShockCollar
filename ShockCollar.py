#!/usr/bin/env python
#07/09/2017 rjmendez
import binascii, bitstring, sys, rflib

input_hex = ''
output_hex = ''
output_bin = ''

'''
08|7|535e3|f7|8|aca1c
level|rxid|sysid|ff-level|f-rxid|fffff-sysid
level: 01-64 (1-100)
rxid 1: Shock collar 1
rxid 3: Shock collar 2
rxid 5: Vibrate collar 1
rxid 7: Vibrate collar 2
rxid 9: Tone collar 1
rxid b: Tone collar 2
rxid d: Light collar 1
rxid f: Light collar 2
'''

#Radio stuff
frequency = 433945000
baudRate = 3600
keyLen = 0
d = rflib.RfCat()
sysid = 341475
rxid = int(sys.argv[2])
level = int(sys.argv[1])
rxid_list = [1, 3, 5, 7, 9, 11, 13, 15]
#Activate packet spoiler for extra speed!
#Sequence of bits will set the end of stream and correct timing of pulses.
data_spoiler = "110000000000000000000000000000000000000000"

def ConfigureD(d):
    d.setMdmModulation(rflib.MOD_ASK_OOK)
    d.setFreq(frequency)
    d.makePktFLEN(keyLen)
    d.setMdmDRate(baudRate)
    d.setMaxPower()
    d.lowball()
#Some modes (tone and blinking light) don't support power levels. 
if rxid not in rxid_list:
    print("Bad rxid, valid values are.\n" + str(rxid_list))
    quit()
if rxid in [9, 11, 13, 15]:
    print('Setting Power Level to 1.\nCurrent rxid setting: ' + str(rxid) + ' does not support power levels!')
    level = 1
#Max power is 100%, the protocol supports 255 however the device does not. :(
if level <= 100:
    print("Power Level set: " + str(level))
if level > 100:
    print("Invalid Power Level Detected!\nPower must be set from 1 to 100, sorry dude!")
    level = 100
    print("Power Level set: " + str(level))
#Lets make sure there is an even number of characters.
if level >= 16:
    input_hex = str(hex(level).lstrip("0x") + hex(rxid).lstrip("0x") + hex(sysid).lstrip("0x") + hex(255-level).lstrip("0x") + hex(15-rxid).lstrip("0x") + hex(1048575-sysid).lstrip("0x"))
if level <= 15:
    input_hex = str('0' + hex(level).lstrip("0x") + hex(rxid).lstrip("0x") + hex(sysid).lstrip("0x") + hex(255-level).lstrip("0x") + hex(15-rxid).lstrip("0x") + hex(1048575-sysid).lstrip("0x"))

#Bytes to Bits ascii stream.
def byte_to_binary(n):
    return ''.join(str((n & (1 << i)) and 1) for i in reversed(range(8)))
#Hex to Bytes.
def hex_to_binary(h):
    return ''.join(byte_to_binary(ord(b)) for b in binascii.unhexlify(h))
#Convert hex to binary ascii stream
input_bin = hex_to_binary(input_hex)

#Convert binary data to format that the radio is expecting. 1 = 1110 0 = 1000
for bit in input_bin:
    if bit == '0':
        output_bin += '1000'
    elif bit == '1':
        output_bin += '1110'
    else:
        print("lolwut?")

rf_data = bitstring.BitArray(bin=output_bin+data_spoiler).tobytes()
keyLen = len(rf_data)
#Configure Radio here.
ConfigureD(d)
#Transmit here.
print('Sending packet payload 3*: ' + input_hex)
d.RFxmit(rf_data, repeat=3)
d.setModeIDLE()
print('Done!')
quit()

