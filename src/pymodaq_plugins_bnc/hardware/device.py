import telnetlib
import time

class Device:
    def __init__(self, ip, port):
        self.com = telnetlib.Telnet(ip, port, 100)
        self.ip = ip
        self.port = port

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
                self.com.open(self.ip, self.port, 100)
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

