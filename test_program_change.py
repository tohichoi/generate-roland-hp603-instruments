import time
import rtmidi

# 15488 : 
# Take the value of Controller 0, multiply it by 128,
# add the value of Controller 32 to derive the bank number.

# CONCERT PIANO 0 68 0
# BANK: 0 * 128 + 68
# PATCH: 0
# EP BELLE 8 68 5
# BANK: 8 * 128 + 68 = 1092
# PATCH 5

# c0 * 128 + c32 = 15488
# c0 * 128 + c32 = 15489
# c0 * 128 = 15488-c32
# c0 = (15488-c32) / 128


midiout = rtmidi.MidiOut()
available_ports = midiout.get_ports()

if available_ports:
    midiout.open_port(1)
else:
    midiout.open_virtual_port("Roland Digital Piano 1")


# GM2
sysex=[0xf0, 0x7e, 0x7f, 0x09, 0x03, 0xf7]
midiout.send_message(sysex)


while True:
    ret=input('Enter CC#0, CC#32, PC# : ').strip().split()
    if len(ret) < 3:
        break
    msb, lsb, inst=map(int, ret)

    # control, bank, msb, 
    pc_msb=[ 0xb0, 0, msb ]
    pc_lsb=[ 0xb0, 32, lsb ]
    pc=[ 0xc0, inst ]
    midiout.send_message(pc_msb)
    midiout.send_message(pc_lsb)
    midiout.send_message(pc)

    note_on = [0x90, 67, 80] # channel 1, middle C, velocity 60
    note_off = [0x80, 67, 0]
    midiout.send_message(note_on)
    time.sleep(0.5)
    midiout.send_message(note_off)
    # time.sleep(0.1)

    note_on = [0x90, 60, 50] # channel 1, middle G, velocity 80
    note_off = [0x80, 60, 0]
    midiout.send_message(note_on)
    time.sleep(1)
    midiout.send_message(note_off)
    time.sleep(0.1)

del midiout
