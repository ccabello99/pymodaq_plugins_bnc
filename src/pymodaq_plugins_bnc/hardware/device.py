import telnetlib
from qtpy.QtCore import QObject, Signal

class Device:
    def __init__(self, ip, port):
        self.com = telnetlib.Telnet(ip, port, 100)
        self._ip = ip
        self._port = port
        self.listener = self.DeviceListener()
        self.still_communicating = False

    def send(self, msg):
        sent = False
        msg += "\r\n"
        self.listener.still_communicating.emit(True)
        try:
            while not sent:
                try:
                    self.com.write(msg.encode())
                    print("SENDING:", msg)
                    sent = True
                    message = self.com.read_until(b"\n", timeout=1).decode().strip()
                    self.listener.ok_received.emit()
                    print("RECEIVED:", message)
                except OSError:
                    self.com.open(self._ip, self._port, 100)
            return message
        finally:
            self.listener.still_communicating.emit(False)

    def query(self,msg):
        msg = msg+"?"
        return self.send(msg)

    def set(self, msg, val):
        msg = msg+" "+val
        return self.send(msg)

    def concat(self, commands):
        msg = ""
        for i in commands:
            msg += ":"+i
        return msg
    
    class DeviceListener(QObject):
        ok_received = Signal()
        still_communicating = Signal(bool)