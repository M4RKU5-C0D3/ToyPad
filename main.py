#!/usr/bin/env /home/martens/.local/bin/ToyPad/.venv/bin/python
import os
import threading
import time
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from notifypy import Notify
from playsound import playsound
from pomodoro import pomodoro
from toypad import ToyPad

# Lade Umgebungsvariablen aus .env Datei
load_dotenv()

# Sound-Konstanten
SOUND_DEFAULT = '/usr/share/sounds/Yaru/stereo/bell.oga'
SOUND_DEVICE_ADDED = '/usr/share/sounds/Yaru/stereo/device-added.oga'
SOUND_DEVICE_REMOVED = '/usr/share/sounds/Yaru/stereo/device-removed.oga'
SOUND_POMODORO = '/usr/share/sounds/ubuntu/notifications/Mallet.ogg'

# Pfad-Konstanten
SCRIPT_CLIQ_AFK = '/home/martens/apps/zoho/cliq/afk.sh'
SCRIPT_CLIQ_DND = '/home/martens/apps/zoho/cliq/dnd.sh'
SCRIPT_CLIQ_READY = '/home/martens/apps/zoho/cliq/re.sh'
SCRIPT_LUNCH = '/home/martens/apps/mittag.sh'
SCRIPT_MEET_MENU = '/home/martens/apps/meet/menu.sh'
SCRIPT_RETURN = '/home/martens/apps/return.sh'

class StatusHandler:
    def __init__(self, toy_pad: ToyPad, mqtt_client):
        self.toy_pad = toy_pad
        self.mqtt_client = mqtt_client

    @staticmethod
    def _launch_with_sound(command, sound=DEFAULT_SOUND):
        threading.Thread(target=os.system, args=(command,)).start()
        playsound(sound)

    def handle_available(self, pad, pid, tid, action):
        print('Available:', pid, tid, action)
        self.mqtt_client.publish("toypad/event", "available")
        self._launch_with_sound(CLIQ_READY_SCRIPT, DEVICE_ADDED_SOUND)
        pad.flash(pid, pad.GREEN)

    def handle_away(self, pad, pid, tid, action):
        print('Away:', pid, tid, action)
        self.mqtt_client.publish("toypad/event", "away")
        self._launch_with_sound(CLIQ_AFK_SCRIPT, DEVICE_REMOVED_SOUND)
        pad.flash(pid, pad.YELLOW)

    def handle_busy(self, pad, pid, tid, action):
        print('Busy: ', pid, tid, action)
        self.mqtt_client.publish("toypad/event", "busy")
        self._launch_with_sound(MEET_MENU_SCRIPT)
        pad.flash(pid, pad.RED)

    def handle_dnd(self, pad, pid, tid, action):
        print('DND: ', pid, tid, action)
        self.mqtt_client.publish("toypad/event", "dnd")
        self._launch_with_sound(CLIQ_DND_SCRIPT)
        pad.flash(pid, pad.RED)

    def handle_lunch(self, pad, pid, tid, action):
        print('Lunch: ', pid, tid, action)
        self.mqtt_client.publish("toypad/event", "lunch")
        self._launch_with_sound(LUNCH_SCRIPT, DEVICE_REMOVED_SOUND)
        pad.flash(pid, pad.RED)

    def handle_return(self, pad, pid, tid, action):
        print('Return:', pid, tid, action)
        self.mqtt_client.publish("toypad/event", "return")
        self._launch_with_sound(RETURN_SCRIPT, DEVICE_ADDED_SOUND)
        pad.flash(pid, pad.GREEN)


class PomodoroHandler:
    def __init__(self, toy_pad: ToyPad):
        self.toy_pad = toy_pad

    def handle_break(self, pomodoro_instance):
        print('break:', pomodoro_instance)
        self.toy_pad.color(self.toy_pad.ALL, self.toy_pad.RED)
        Notify('Pomodoro', 'Take a break!').send()
        playsound(POMODORO_SOUND)

    def handle_work(self, pomodoro_instance):
        print('work:', pomodoro_instance)
        self.toy_pad.color(self.toy_pad.ALL, self.toy_pad.OFF)
        Notify('Pomodoro', 'Get back to work...').send()
        playsound(POMODORO_SOUND)


def create_mqtt_client():
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqtt_client.on_connect = lambda client, userdata, flags, reason_code, properties: (
        print(f"Connected with result code {reason_code}"),
        client.publish("toypad/event", "connected")
    )
    mqtt_client.username_pw_set(
        os.getenv('MQTT_USERNAME'),
        os.getenv('MQTT_PASSWORD')
    )
    mqtt_client.connect(
        os.getenv('MQTT_HOST', 'localhost'),
        int(os.getenv('MQTT_PORT', '1883')),
        60
    )
    return mqtt_client


def configure_token_actions(toy_pad: ToyPad, status_handler: StatusHandler):
    actions = {
        toy_pad.TID_Markus: {
            toy_pad.LEFT: {
                toy_pad.INSERT: status_handler.handle_busy,
                toy_pad.REMOVE: status_handler.handle_away
            },
            toy_pad.CENTER: {
                toy_pad.INSERT: status_handler.handle_available,
                toy_pad.REMOVE: status_handler.handle_away
            },
            toy_pad.RIGHT: {
                toy_pad.INSERT: status_handler.handle_dnd,
                toy_pad.REMOVE: status_handler.handle_away
            }
        },
        toy_pad.TID_Carrot: {
            toy_pad.CENTER: {
                toy_pad.INSERT: status_handler.handle_lunch,
                toy_pad.REMOVE: status_handler.handle_return
            }
        }
    }

    for token_id, pad_configs in actions.items():
        for pad_pos, event_configs in pad_configs.items():
            for event_type, action_func in event_configs.items():
                toy_pad.on(pad_pos, token_id, event_type, action_func)


def main():
    toy_pad = ToyPad()
    while not toy_pad.connect():
        time.sleep(5)
    toy_pad.flash(toy_pad.ALL, toy_pad.GREEN)

    mqtt_client = create_mqtt_client()
    mqtt_client.loop_start()

    status_handler = StatusHandler(toy_pad, mqtt_client)
    configure_token_actions(toy_pad, status_handler)

    pomodoro_timer = pomodoro(28, 2)
    pomodoro_handler = PomodoroHandler(toy_pad)
    pomodoro_timer.on('break', pomodoro_handler.handle_break)
    pomodoro_timer.on('work', pomodoro_handler.handle_work)

    Notify('ToyPad', 'Ready...').send()

    while True:
        toy_pad.tick()
        pomodoro_timer.tick()


if __name__ == '__main__':
    main()
