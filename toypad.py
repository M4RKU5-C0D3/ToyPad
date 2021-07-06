#
# https://www.kite.com/python/answers/how-to-import-a-class-from-another-file-in-python
#
import usb.core
import usb.util
import numpy as np

class toypad:

    INIT   = [0x55, 0x0f, 0xb0, 0x01, 0x28, 0x63, 0x29, 0x20, 0x4c, 0x45, 0x47, 0x4f, 0x20, 0x32, 0x30, 0x31, 0x34, 0xf7, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    # PADS
    ALL    = 0
    CENTER = 1
    LEFT   = 2
    RIGHT  = 3
    # TAGS
    INSERT = 0
    REMOVE = 1
    # COLORS
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

    TID_Gandalf      = "04167DD2A14081"
    TID_WildStyle    = "044DB2FA9D4880"
    TID_Badman       = "04F3439A134380"
    TID_Abbey        = "04677292284980"
    TID_Custom01     = "044731F27C4981"
    TID_BadCop       = "0441651AA34880"
    TID_Benny        = "049E0E325C4984"
    TID_Chase        = "0473FF5AA74A80"
    TID_Markus       = "045ACC125D4981"

    events = {}

    def __init__(self):
        global dev
        dev = usb.core.find(idVendor=0x0e6f, idProduct=0x0241)
        if dev is None:
            print('Device not found')
        else:
            if dev.is_kernel_driver_active(0):
                dev.detach_kernel_driver(0)
            print((usb.util.get_string(dev, dev.iProduct)))
            dev.set_configuration()
            dev.write(1,self.INIT)

    def dev(self):
        global dev
        return dev

    def tidstr(self,uid):
        uid = np.array(uid)
        uid = ("{:0>2X}"*len(uid)).format(*tuple(uid))
        return uid

    def command(self,command):
        global dev
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

    def color(self, pad, color):
        self.command([0x55, 0x06, 0xc0, 0x02, pad, color[0], color[1], color[2]])
        return

    def ekey(self,pid,tid,action):
        return '{}{}{}'.format(pid,tid,action)

    def on(self, pid,tid,action, _callback = None):
        self.events[self.ekey(pid,tid,action)] = _callback;

    def trigger(self, pid,tid,action):
        print(pid,tid,action)
        if self.ekey(pid,tid,action) in self.events:
            self.events[self.ekey(pid,tid,action)](self)

    def tick(self):
        global dev
        try:
            packet = dev.read(0x81, 32, timeout = 10)
            bytelist = list(packet)
            if not bytelist:
                pass
            elif bytelist[0] != 0x56: # NFC packets start with 0x56
                pass
            else:
                pid = bytelist[2] # = Pad ID
                tid = self.tidstr(bytelist[6:13]) # = Tag ID
                action = bytelist[5]
                self.trigger(pid,tid,action)
        except usb.USBError as err:
            pass
        return
