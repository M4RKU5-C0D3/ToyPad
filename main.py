#!/usr/bin/env python3

from sys import intern
from toypad import toypad
import usb.core
import usb.util
import numpy as np
import os
import subprocess
import time
import datetime as dt

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
        print(now,'have a break')
    if pom_work < now: # start working
        pom_work = pom_break + dt.timedelta(0,60*2) # start next work 2 minutes after next break
        pad_color(CENTER_PAD,OFF)
        print(now,'start working')

    # if pad_toggle:
    #     pad_toggle = False
    #     pad_color(RIGHT_PAD,[0xFF,0x00,0x00])
    # else:
    #     pad_toggle = True
    #     pad_color(RIGHT_PAD,OFF)

    now = dt.datetime.now()
    return


def main():
    pad = toypad()
    np.set_printoptions(formatter={'int':hex})
    if pad.dev() != None :
        while True:
            pad.tick()
            time.sleep(0.5)
    return

if __name__ == '__main__':
    main()
