# ShockCollar
RFcat "Dog Training Collar" controller

Example packet breakdown.

08|7|535e3|f7|8|aca1c

level|rxid|sysid|ff-level|f-rxid|fffff-sysid

It seems that it verifies the packet is valid by subtracting the first 8
bytes from 8 bytes of FF and comparing that to the last 8 bytes in this
packet followed by a binary 11 in the radio baseband.

level: 01-64 (1-100)

rxid 1: Shock collar 1

rxid 3: Shock collar 2

rxid 5: Vibrate collar 1

rxid 7: Vibrate collar 2

rxid 9: Tone collar 1

rxid b: Tone collar 2

rxid d: Light collar 1

rxid f: Light collar 2

sysid: The device I have has this set, unsure if this changes between
transmitters.

Use:

sudo ShockCollar.py [power level] [reciever ID/mode]

Some modes do not support power levels like the chirping tone and the
flashing LED. The protocol supports values greater than 100 on vibrate
and "static shock" modes but the devices seem to drop these packets.
