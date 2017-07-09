#!/usr/bin/env python
#07/09/2017 rjmendez
import binascii, bitstring, sys, getopt, rflib

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
#Help
help_msg = 'ShockCollar.py -l <level> -r <reciever> -s <systemid>\n\nLevel\nInteger: 1-100\n\nReciever Codes\n1: Shock collar 1\n3: Shock collar 2\n5: Vibrate collar 1\n7: Vibrate collar 2\n9: Tone collar 1\n11: Tone collar 2\n13: Light collar 1\n15: Light collar 2\n\nSystem ID\nInteger: 1-1048575'

#Radio stuff
frequency = 433945000
baudRate = 3600
keyLen = 0
#d = rflib.RfCat()
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

#Padding the input values.
def PadBytes(byte_length, hex_val):
    #print(str(byte_length-len(hex_val)))
    pad_num = byte_length-len(hex_val)
    if pad_num >= 1:
        pad_str = "0" * pad_num
        #print(pad_str)
        padded_hex_val = str(pad_str + hex_val)
        #print(padded_hex_val)
        return padded_hex_val
    if pad_num == 0:
        #do nothing
        padded_hex_val = hex_val
        return padded_hex_val
    if pad_num < 0:
        print('Invalid length of input, was expecting <= ' + str(byte_length) + ' but we got ' + str(len(hex_val)) + ' instead!')
        print(help_msg)
        quit()

def PacketValues(level, rxid, sysid):
    hex_level = PadBytes(2, str(hex(level)).lstrip("0x"))
    #print(hex_level)
    hex_rxid = PadBytes(1, str(hex(rxid)).lstrip("0x"))
    #print(hex_rxid)
    hex_sysid = PadBytes(5, str(hex(sysid)).lstrip("0x"))
    #print(hex_sysid)
    #Calculate checksums.
    calc_level = 255-level
    calc_rxid = 15-rxid
    calc_sysid = 1048575-sysid
    #Return hex values.
    check_level = PadBytes(2, str(hex(calc_level)).lstrip("0x"))
    #print(check_level)
    check_rxid = PadBytes(1, str(hex(calc_rxid)).lstrip("0x"))
    #print(check_rxid)
    check_sysid = PadBytes(5, str(hex(calc_sysid)).lstrip("0x"))
    #print(check_sysid)
    input_hex = hex_level + hex_rxid + hex_sysid + check_level + check_rxid + check_sysid
    #print('test ' + input_hex)
    return input_hex

def ValidateInputs(level, rxid, sysid):
    #Some modes (tone and blinking light) don't support power levels. 
    if rxid not in rxid_list:
        print("Bad reciever id value!")
        print(help_msg)
        quit()
    if rxid in [9, 11, 13, 15]:
        print('Setting Power Level to 1.\nCurrent rxid setting: ' + str(rxid) + ' does not support power levels!')
        level = 1
        #return level
    #Max power is 100%, the protocol supports 255 however the device does not. :(
    if level <= 100:
        print("Power Level set: " + str(level))
        #return level
    if level > 100:
        print("Invalid Power Level Detected!\nPower must be set from 1 to 100, sorry dude!")
        level = 100
        print("Power Level set: " + str(level))
        #return level
    if sysid >= 1048576:
        print("Invalid System ID Detected!")
        print(help_msg)
        quit()
    if sysid <= 1048575:
        return level, rxid, sysid

#Bytes to Bits ascii stream.
def byte_to_binary(n):
    return ''.join(str((n & (1 << i)) and 1) for i in reversed(range(8)))
#Hex to Bytes.
def hex_to_binary(h):
    return ''.join(byte_to_binary(ord(b)) for b in binascii.unhexlify(h))

def main(argv):
    level = 1
    rxid = ''
    sysid = ''
    input_hex = ''
    output_hex = ''
    output_bin = ''
    try:
        opts, args = getopt.getopt(argv,"hl:r:s:",["level=","reciever=","systemid"])
    except getopt.GetoptError as error:
        print(error)
        print(help_msg)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(help_msg)
            sys.exit()
        elif opt in ("-l", "--level"):
            level = int(arg)
        elif opt in ("-r", "--reciever"):
            rxid = int(arg)
        elif opt in ("-s", "--systemid"):
            sysid = int(arg)
    if len(sys.argv) == 1:
        print('Invalid input, program accepts the following input format:\n' + help_msg)
        sys.exit(2)


    level, rxid, sysid = ValidateInputs(level, rxid, sysid)
    #Generate packet hex
    input_hex = PacketValues(level, rxid, sysid)
    
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
    d = rflib.RfCat()
    ConfigureD(d)
    #Transmit here.
    print('Sending packet payload 4*: ' + input_hex)
    d.RFxmit(rf_data, repeat=3)
    d.setModeIDLE()
    print('Done!')
    quit()


if __name__ == "__main__":
    main(sys.argv[1:])

