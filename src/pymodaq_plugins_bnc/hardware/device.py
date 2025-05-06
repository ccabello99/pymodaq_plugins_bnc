import telnetlib
import time
from qtpy import QtCore

class Device:
    def __init__(self, ip, port):
        self.com = telnetlib.Telnet(ip, port, 100)
        self._ip = ip
        self._port = port
        self.listener = self.DeviceListener()

    def send(self, msg):
        sent = False
        msg += "\r\n"
        while not sent:
            try:
                self.com.write(msg.encode())
                print("SENDING:", msg)
                sent = True
                time.sleep(0.075)
                message = self.com.read_eager().decode()
                print("RECEIVED:", message)
            except OSError:
                self.com.open(self._ip, self._port, 100)
        if message == 'ok':
            self.listener.ok_received.emit()
        return message

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
    
    class DeviceListener(QtCore.QObject):
        ok_received = QtCore.pyqtSignal()