#!/usr/bin/env python3

from sys import intern
from toypad import toypad
from pomodoro import pomodoro
import usb.core
import usb.util
import os
import subprocess
import time

def available(pad: toypad):
    print('Available')
    pad.color(pad.CENTER,pad.OFF)

def offline(pad: toypad):
    print('Offline')
    pad.color(pad.CENTER,pad.RED)

def main():
    pad = toypad()
    pad.on(pad.CENTER,pad.TID_Markus,pad.INSERT,available)
    pad.on(pad.CENTER,pad.TID_Markus,pad.REMOVE,offline)
    pom = pomodoro()
    while True:
        pad.tick()
        pom.tick()
    return

if __name__ == '__main__':
    main()
