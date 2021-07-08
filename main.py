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

def pom_break(pom: pomodoro):
    global pad
    print('break:',pom)
    pad.color(pad.ALL,pad.RED)

def pom_work(pom: pomodoro):
    global pad
    print('work:',pom)
    pad.color(pad.ALL,pad.OFF)

def main():
    global pad,pom
    pad = toypad()
    pad.on(pad.CENTER,pad.TID_Markus,pad.INSERT,available)
    pad.on(pad.CENTER,pad.TID_Markus,pad.REMOVE,offline)
    pom = pomodoro(28,2)
    pom.on('break',pom_break)
    pom.on('work',pom_work)
    while True:
        pad.tick()
        pom.tick()
    return

if __name__ == '__main__':
    main()
