#!/usr/bin/env python3

import usb.core
import usb.util
import numpy as np
import os
from time import sleep

TOYPAD_INIT = [0x55, 0x0f, 0xb0, 0x01, 0x28, 0x63, 0x29, 0x20, 0x4c, 0x45, 0x47, 0x4f, 0x20, 0x32, 0x30, 0x31, 0x34, 0xf7, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

OFF    = [0x00,0x00,0x00]
RED    = [0xFF,0x00,0x00]
GREEN  = [0x00,0xFF,0x00]
BLUE   = [0x00,0x00,0xFF]
ORANGE = [0xFF,0x11,0x00]
YELLOW = [0xAA,0x33,0x00]
PINK   = [0xFF,0x00,0x33]
TEAL   = [0x33,0xFF,0xFF]
PURPLE = [0x33,0x00,0xFF]
WHITE  = [0xFF,0xFF,0xFF]

ALL_PADS   = 0
CENTER_PAD = 1
LEFT_PAD   = 2
RIGHT_PAD  = 3

# Actions
TAG_INSERTED = 0
TAG_REMOVED  = 1

uidGandalf      = [0x04,0x16,0x7D,0xD2,0xA1,0x40,0x81]
uidWildStyle    = [0x04,0x4D,0xB2,0xFA,0x9D,0x48,0x80]
uidBadman       = [0x04,0xF3,0x43,0x9A,0x13,0x43,0x80]
uidAbbey        = [0x04,0x67,0x72,0x92,0x28,0x49,0x80]
uidCustom01     = [0x04,0x47,0x31,0xF2,0x7C,0x49,0x81]
uidBadCop       = [0x04,0x41,0x65,0x1A,0xA3,0x48,0x80]
uidBenny        = [0x04,0x9E,0xE0,0x32,0x5C,0x49,0x84]
uidChase        = [0x04,0x73,0xFF,0x5A,0xA7,0x4A,0x80]

def init_usb():
    global dev

    dev = usb.core.find(idVendor=0x0e6f, idProduct=0x0241)

    if dev is None:
        print('Device not found')
    else:
        if dev.is_kernel_driver_active(0):
            dev.detach_kernel_driver(0)

        print((usb.util.get_string(dev, dev.iProduct)))

        dev.set_configuration()
        dev.write(1,TOYPAD_INIT)

    return dev


def send_command(dev,command):

    # calculate checksum
    checksum = 0
    for word in command:
        checksum = checksum + word
        if checksum >= 256:
            checksum -= 256
        message = command+[checksum]

    # pad message
    while(len(message) < 32):
        message.append(0x00)

    # send message
    dev.write(1, message)

    return


def switch_pad(pad, colour):
    send_command(dev,[0x55, 0x06, 0xc0, 0x02, pad, colour[0], colour[1], colour[2],])
    return


def uid_compare(uid1, uid2):
    match = True
    for i in range(0,7):
        if (uid1[i] != uid2[i]) :
            match = False
    return match 

def tag_inserted(pad_num,uid_bytes):
    print(np.array(uid_bytes),'detected on pad',pad_num)
    if uid_compare(uid_bytes,uidCustom01): 
        switch_pad(pad_num, WHITE)
        os.system("echo 'Available'")
    elif uid_compare(uid_bytes, uidGandalf): switch_pad(pad_num, YELLOW)
    elif uid_compare(uid_bytes, uidBadCop): switch_pad(pad_num, ORANGE)
    elif uid_compare(uid_bytes, uidWildStyle): switch_pad(pad_num, PINK)
    elif uid_compare(uid_bytes, uidBadman): switch_pad(pad_num, BLUE)
    elif uid_compare(uid_bytes, uidAbbey): switch_pad(pad_num, TEAL)
    elif uid_compare(uid_bytes, uidBenny): switch_pad(pad_num, GREEN)
    elif uid_compare(uid_bytes, uidChase): switch_pad(pad_num, PURPLE)
    else: switch_pad(pad_num, RED)
    return

def tag_removed(pad_num,uid_bytes):
    print(np.array(uid_bytes),'removed from pad',pad_num)
    if uid_compare(uid_bytes,uidCustom01): 
        os.system("echo 'Unavailable'")
    switch_pad(pad_num, OFF)
    return

def main():
    init_usb()
    np.set_printoptions(formatter={'int':hex})
    if dev != None :
        while True:
            try:
                in_packet = dev.read(0x81, 32, timeout = 10)
                bytelist = list(in_packet)

                if not bytelist:
                    pass
                elif bytelist[0] != 0x56: # NFC packets start with 0x56
                    pass
                else:
                    pad_num = bytelist[2]
                    uid_bytes = bytelist[6:13]
                    action = bytelist[5]
                    if action == TAG_INSERTED :
                        tag_inserted(pad_num,uid_bytes)
                    else:
                        tag_removed(pad_num,uid_bytes)

            except usb.USBError as err:
                pass

        switch_pad(ALL_PADS,OFF)
    return

if __name__ == '__main__':
    main()
