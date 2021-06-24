#!/usr/bin/env python3

from sys import intern
import usb.core
import usb.util
import numpy as np
import os
import subprocess
import time
import datetime as dt

#from .pad import pad

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

uidGandalf      = "04167DD2A14081"
uidWildStyle    = "044DB2FA9D4880"
uidBadman       = "04F3439A134380"
uidAbbey        = "04677292284980"
uidCustom01     = "044731F27C4981"
uidBadCop       = "0441651AA34880"
uidBenny        = "049E0E325C4984"
uidChase        = "0473FF5AA74A80"
uidMarkus       = "045ACC125D4981"

def uid_str(uid):
    uid = np.array(uid)
    uid = ("{:0>2X}"*len(uid)).format(*tuple(uid))
    return uid

def presence(present,pad,uid):    
    # TODO: contact API
    return

# PAD:

def pad_init():
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

def pad_command(dev,command):

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

def pad_color(pad, colour):
    pad_command(dev,[0x55, 0x06, 0xc0, 0x02, pad, colour[0], colour[1], colour[2],])
    return

def pad_detected(pad,uid):
    print(uid,'detected on pad',pad)
    if uid == uidMarkus: 
        pad_color(pad, WHITE)
        if pad == CENTER_PAD: presence(True,pad,uid)
    elif uid == uidGandalf   : pad_color(pad, YELLOW)
    elif uid == uidBadCop    : pad_color(pad, ORANGE)
    elif uid == uidWildStyle : pad_color(pad, PINK)
    elif uid == uidBadman    : pad_color(pad, BLUE)
    elif uid == uidAbbey     : pad_color(pad, TEAL)
    elif uid == uidBenny     : pad_color(pad, GREEN)
    elif uid == uidChase     : pad_color(pad, PURPLE)
    else: pad_color(pad, RED)
    time.sleep(1)
    pad_color(ALL_PADS,OFF)
    return

def pad_removed(pad,uid):
    print(uid,'removed from pad',pad)
    if uid == uidCustom01:
        if pad == CENTER_PAD: presence(False,pad,uid)
    pad_color(pad, OFF)
    return

def pad_tick():
    try:
        in_packet = dev.read(0x81, 32, timeout = 10)
        bytelist = list(in_packet)
        if not bytelist:
            pass
        elif bytelist[0] != 0x56: # NFC packets start with 0x56
            pass
        else:
            pad = bytelist[2]
            uid = uid_str(bytelist[6:13])
            action = bytelist[5]
            if   action == TAG_INSERTED : pad_detected(pad,uid)
            elif action == TAG_REMOVED  : pad_removed(pad,uid)
            else : print('unkown action: ' + action)
    except usb.USBError as err:
        pass
    return

# POM:

def pom_init():
    global now, pom_break, pom_work
    now = dt.datetime.now()
    pom_break = dt.datetime.now()
    pom_work = dt.datetime.now()
    return

pad_toggle = False
def pom_tick():
    global now, pom_break, pom_work, pad_toggle

    if pom_break < now: # start break
        pom_break = now + dt.timedelta(0,60*28) # start next break 28 minutes after now
        pad_color(CENTER_PAD,[0xFF,0x00,0x00])
        print('have a break')
    if pom_work < now: # start working
        pom_work = pom_break + dt.timedelta(0,60*2) # start next work 2 minutes after next break
        pad_color(CENTER_PAD,OFF)
        print('start working')

    # if pad_toggle:
    #     pad_toggle = False
    #     pad_color(RIGHT_PAD,[0xFF,0x00,0x00])
    # else:
    #     pad_toggle = True
    #     pad_color(RIGHT_PAD,OFF)

    now = dt.datetime.now()
    return

# MAIN:

def main():
    pad_init()
    pom_init()
    np.set_printoptions(formatter={'int':hex})
    if dev != None :
        while True:
            pad_tick()
            pom_tick()
            time.sleep(0.5)
    return

if __name__ == '__main__':
    main()
