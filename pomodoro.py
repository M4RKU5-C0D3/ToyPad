import datetime as dt

class pomodoro:

    events = {}

    def __init__(self):
        global now, pom_break, pom_work
        now = dt.datetime.now()
        pom_break = dt.datetime.now()
        pom_work = dt.datetime.now()
        return

    def on(self, event, _callback = None):
        self.events[event] = _callback;

    def trigger(self, event):
        return

    def tick(self):
        global now, pom_break, pom_work
        if pom_break < now: # start break
            pom_break = now + dt.timedelta(0,60*28) # start next break 28 minutes after now
            print(now,'have a break')
        if pom_work < now: # start working
            pom_work = pom_break + dt.timedelta(0,60*2) # start next work 2 minutes after next break
            print(now,'start working')
        now = dt.datetime.now()
        return
