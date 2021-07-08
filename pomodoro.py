import datetime as dt

class pomodoro:

    events = {}
    t_work = 0  # minutes
    t_break = 0 # minutes

    def __init__(self,t_work,t_break):
        global now, pom_break, pom_work
        self.t_work = t_work
        self.t_break = t_break
        now = dt.datetime.now()
        pom_break = dt.datetime.now()
        pom_work = dt.datetime.now()
        return

    def on(self, event, _callback = None):
        self.events[event] = _callback;

    def trigger(self, event):
        if event in self.events:
            self.events[event](self)

    def tick(self):
        global now, pom_break, pom_work
        if pom_break < now: # start break
            pom_break = now + dt.timedelta(0,60*self.t_work) # start next break X minutes after now
            self.trigger('break')
        if pom_work < now: # start working
            pom_work = pom_break + dt.timedelta(0,60*self.t_break) # start next work X minutes after next break
            self.trigger('work')
        now = dt.datetime.now()
        return
