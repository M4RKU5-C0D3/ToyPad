#!/usr/bin/env python3

from sys import intern
from toypad import ToyPad
from pomodoro import pomodoro
import os


# region status
def available(pad: ToyPad, pid, tid, action):
    print('Available:', pid, tid, action)
    os.system('/home/martens/apps/zoho/cliq/re.sh')
    pad.flash(pid, pad.GREEN)


def away(pad: ToyPad, pid, tid, action):
    print('Away:', pid, tid, action)
    os.system('/home/martens/apps/zoho/cliq/afk.sh')
    pad.flash(pid, pad.YELLOW)


def busy(pad: ToyPad, pid, tid, action):
    print('Busy: ', pid, tid, action)
    os.system('/home/martens/apps/zoho/cliq/busy.sh "Meeting"')
    pad.flash(pid, pad.RED)


# endregion


# region pom
def pom_break(pom: pomodoro):
    global pad
    print('break:', pom)
    pad.color(pad.ALL, pad.RED)


def pom_work(pom: pomodoro):
    global pad
    print('work:', pom)
    pad.color(pad.ALL, pad.OFF)


# endregion


def main():
    global pad, pom
    pad = ToyPad()
    pad.flash(pad.ALL, pad.GREEN)
    pad.on(pad.CENTER, pad.TID_Markus, pad.REMOVE, away)
    pad.on(pad.CENTER, pad.TID_Markus, pad.INSERT, available)
    pad.on(pad.LEFT, pad.TID_Markus, pad.INSERT, busy)
    pom = pomodoro(28, 2)
    pom.on('break', pom_break)
    pom.on('work', pom_work)
    while True:
        pad.tick()
        pom.tick()
    return


if __name__ == '__main__':
    main()
