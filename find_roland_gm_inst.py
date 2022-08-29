#!/usr/bin/env python
"""
Send random notes to the output port.
"""

from __future__ import print_function
import sys
import time
import random
import mido
from mido import Message


print('Output ports:')
print('\n'.join(mido.get_output_names()))

if len(sys.argv) > 1:
    portname = sys.argv[1]
else:
    portname = None  # Use default port


def send_gm2_sysex(port):
    sysex=[0xf0, 0x7e, 0x7f, 0x09, 0x03, 0xf7]
    msg1 = mido.Message.from_bytes(sysex)
    port.send(msg1)


def get_cc_msg(val):

    idx=0
    pcmsg=[]
    pcmsg.append(Message('control_change', control=int(val.pop())))
    pcmsg.append(Message('control_change', control=int(val.pop())))
    pcmsg.append(Message('program_change', program=int(val.pop())))

    return pcmsg



def send_test_notes(port, pcmsg):
    # A pentatonic scale
    notes = [60, 62, 64, 65, 67, 69, 71, 
        72, 74, 76, 74, 72, 71, 69, 67, 
        66, 67, 69, 67, 65, 64, 62, 60,
        59]
    delay = [1, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 
        0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5,
        0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 
        2]
    tempo = 0.2
    try:
        # print('Using {}'.format(port))
        for pm in pcmsg:
            port.send(pm)
        for d, note in zip(delay, notes):
        # note = random.choice(notes)
            on = Message('note_on', note=note)
            print('Sending {}'.format(on))
            port.send(on)
            time.sleep(d*tempo)

            off = Message('note_off', note=note)
            print('Sending {}'.format(off))
            port.send(off)
            # time.sleep(0.1)
    except KeyboardInterrupt:
        pass


port=mido.open_output(portname, autoreset=True)
send_gm2_sysex(port)

while True:
    ret=input('Enter CC#0, CC#32, PC# : ').strip().split()
    if len(ret) < 1:
        break
    pcmsg=get_cc_msg(ret)
    # print(' '.join(map(int, pcmsg)))
    send_test_notes(port, pcmsg)

# 15488 : 
# Take the value of Controller 0, multiply it by 128,
# add the value of Controller 32 to derive the bank number.

# c0 * 128 + c32 = 15488
# c0 * 128 + c32 = 15489
# c0 * 128 = 15488-c32
# c0 = (15488-c32) / 128
