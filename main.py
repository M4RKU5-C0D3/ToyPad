#!/usr/bin/env /home/martens/.local/bin/ToyPad/.venv/bin/python

from sys import intern
from toypad import ToyPad
from pomodoro import pomodoro
from playsound import playsound
from notifypy import Notify
import os
import threading
import time
import paho.mqtt.client as mqtt


# region status
def launch(command, sound='/usr/share/sounds/Yaru/stereo/bell.oga'):
    threading.Thread(target=os.system, args=(command,)).start()
    playsound(sound)


def available(pad: ToyPad, pid, tid, action):
    print('Available:', pid, tid, action)
    mqttc.publish("toypad/event", "available")
    launch('/home/martens/apps/zoho/cliq/re.sh', '/usr/share/sounds/Yaru/stereo/device-added.oga')
    pad.flash(pid, pad.GREEN)


def away(pad: ToyPad, pid, tid, action):
    print('Away:', pid, tid, action)
    mqttc.publish("toypad/event", "away")
    launch('/home/martens/apps/zoho/cliq/afk.sh', '/usr/share/sounds/Yaru/stereo/device-removed.oga')
    pad.flash(pid, pad.YELLOW)


def busy(pad: ToyPad, pid, tid, action):
    print('Busy: ', pid, tid, action)
    mqttc.publish("toypad/event", "busy")
    launch('/home/martens/apps/meet/menu.sh')
    pad.flash(pid, pad.RED)


def dnd(pad: ToyPad, pid, tid, action):
    print('DND: ', pid, tid, action)
    mqttc.publish("toypad/event", "dnd")
    launch('/home/martens/apps/zoho/cliq/dnd.sh')
    pad.flash(pid, pad.RED)


def lunch(pad: ToyPad, pid, tid, action):
    print('Lunch: ', pid, tid, action)
    mqttc.publish("toypad/event", "lunch")
    launch('/home/martens/apps/mittag.sh', '/usr/share/sounds/Yaru/stereo/device-removed.oga')
    pad.flash(pid, pad.RED)


def re(pad: ToyPad, pid, tid, action):
    print('Return:', pid, tid, action)
    mqttc.publish("toypad/event", "return")
    launch('/home/martens/apps/return.sh', '/usr/share/sounds/Yaru/stereo/device-added.oga')
    pad.flash(pid, pad.GREEN)


# endregion


# region pom
def pom_break(pom: pomodoro):
    global pad
    print('break:', pom)
    pad.color(pad.ALL, pad.RED)
    Notify('Pomodoro', 'Take a break!').send()
    playsound('/usr/share/sounds/ubuntu/notifications/Mallet.ogg')


def pom_work(pom: pomodoro):
    global pad
    print('work:', pom)
    pad.color(pad.ALL, pad.OFF)
    Notify('Pomodoro', 'Get back to work...').send()
    playsound('/usr/share/sounds/ubuntu/notifications/Mallet.ogg')


# endregion

# region mqtt

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    mqttc.publish("toypad/event", "connected")

# endregion

def main():
    global pad, pom, mqttc
    pad = ToyPad()
    while not pad.connect():
        time.sleep(5)
    pad.flash(pad.ALL, pad.GREEN)
    pad.on(pad.CENTER, pad.TID_Markus, pad.REMOVE, away)
    pad.on(pad.CENTER, pad.TID_Markus, pad.INSERT, available)
    pad.on(pad.LEFT, pad.TID_Markus, pad.INSERT, busy)
    pad.on(pad.RIGHT, pad.TID_Markus, pad.INSERT, dnd)
    pad.on(pad.CENTER, pad.TID_Custom01, pad.INSERT, lunch)
    pad.on(pad.CENTER, pad.TID_Custom01, pad.REMOVE, re)
    pom = pomodoro(28, 2)
    pom.on('break', pom_break)
    pom.on('work', pom_work)
    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttc.on_connect = on_connect
    mqttc.username_pw_set('markus', 'W3FRht9YDJfAxQnr')
    mqttc.connect("xerxes.fritz.box", 1883, 60)
    Notify('ToyPad', 'Ready...').send()
    while True:
        pad.tick()
        pom.tick()

if __name__ == '__main__':
    main()
