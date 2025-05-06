import time
from pymodaq_plugins_bnc.hardware.device import Device
from qtpy import QtCore

class BNC575(Device):

    def __init__(self, ip, port):
        super().__init__(ip, port)
        self.channel_label = "A"
        self.slot = 1
        self.listener.ok_received.connect(self.ok_received)
        self.received = False

    def ok_received(self):
        self.received = True
    
    def check_ok(self):
        start = time.time()
        while not self.received:
            QtCore.QThread.msleep(10)
            if time.time() - start > 3:  # 3-second timeout
                raise TimeoutError("Timeout waiting for device response")
        self.received = False

    def idn(self):
        self.received = False
        idn = self.query("*IDN").strip()
        self.check_ok()
        return idn

    @property
    def ip(self):
        return self._ip

    @property
    def port(self):
        return self._port

    def reset(self):
        self.received = False
        self.send("*RST")
        self.check_ok()

    def stop(self):
        pass
    
    @property
    def slot(self):
        return self._slot
    
    @slot.setter
    def slot(self, slot):
        self._slot = slot
    
    def save_state(self):
        self.received = False
        self.set("*SAV", str(self.slot))
        self.check_ok()
    
    def restore_state(self):
        self.received = False
        self.set("*RCL", str(self.slot))
        self.check_ok()
    
    def trig(self):
        self.received = False
        self.send("*TRG")
        self.check_ok()
    
    @property
    def label(self):
        self.received = False
        lbl = self.query("*LBL").strip()
        self.check_ok()
        return lbl
    
    @label.setter
    def label(self, label):
        self.received = False
        self.set("*LBL", "\"" + label + "\"")
        self.check_ok()
        
    @property
    def global_state(self):
        self.received = False
        state = self.query(":INST:STATE").strip()
        self.check_ok()
        return "ON" if state == "1" else "OFF"

    @global_state.setter
    def global_state(self, state):
        self.received = False
        self.set(":INST:STATE", state)
        self.check_ok()
    
    @property
    def global_mode(self):
        self.received = False
        mode = self.query(":PULSE0:MODE")
        self.check_ok()
        return mode
    
    @global_mode.setter
    def global_mode(self, mode):
        self.received = False
        self.set(":PULSE0:MODE", mode)
        self.check_ok()
        
    def close(self):
        self.listener.ok_received.disconnect(self.ok_received)
        self.com.close()
    
    def set_channel(self):
        return {"A": 1, "B": 2, "C": 3, "D": 4}.get(self.channel_label, 1)

    @property
    def channel_label(self):
        return self._channel_label

    @channel_label.setter
    def channel_label(self, channel_label):
        self._channel_label = channel_label
        
    @property
    def channel_mode(self):
        self.received = False
        channel = self.set_channel()
        mode = self.query(f":PULSE{channel}:CMOD").strip()
        self.check_ok()
        return mode

    @channel_mode.setter
    def channel_mode(self, mode):
        self.received = False
        channel = self.set_channel()
        self.set(f":PULSE{channel}:CMOD", mode)
        self.check_ok()
        
    @property
    def channel_state(self):
        self.received = False
        channel = self.set_channel()
        state = self.query(f":PULSE{channel}:STATE").strip()
        self.check_ok()
        return "ON" if state == "1" else "OFF"

    @channel_state.setter    
    def channel_state(self, state):
        self.received = False
        channel = self.set_channel()
        self.set(f":PULSE{channel}:STATE", state)
        self.check_ok()

    @property
    def trig_mode(self):
        self.received = False
        trig_mode = self.query(":PULSE0:TRIG:MODE").strip()
        self.check_ok()
        return trig_mode

    @trig_mode.setter
    def trig_mode(self, mode):
        self.received = False
        self.set(f":PULSE0:TRIG:MODE", mode)
        self.check_ok()
        
    @property        
    def trig_thresh(self):
        self.received = False
        thresh = float(self.query(":PULSE0:TRIG:LEV").strip())
        self.check_ok()
        return thresh
    
    @trig_thresh.setter
    def trig_thresh(self, thresh):
        self.received = False
        self.set(f":PULSE0:TRIG:LEV", str(thresh))
        self.check_ok()

    @property
    def trig_edge(self):
        self.received = False
        edge = self.query(":PULSE0:TRIG:EDGE").strip()
        self.check_ok()
        return edge
    
    @trig_edge.setter
    def trig_edge(self, edge):
        self.received = False
        self.set(f":PULSE0:TRIG:EDGE", edge)
        self.check_ok()

    @property
    def gate_mode(self):
        self.received = False
        gate_mode = self.query(":PULSE0:GATE:MODE").strip()
        self.check_ok()
        return gate_mode

    @gate_mode.setter
    def gate_mode(self, mode):
        self.received = False
        self.set(f":PULSE0:GATE:MODE", mode)
        self.check_ok()

    @property        
    def gate_thresh(self):
        self.received = False
        thresh = float(self.query(":PULSE0:GATE:LEV").strip())
        self.check_ok()
        return thresh
    
    @gate_thresh.setter
    def gate_thresh(self, thresh):
        self.received = False
        self.set(f":PULSE0:GATE:LEV", str(thresh))
        self.check_ok()

    @property
    def gate_logic(self):
        self.received = False
        global_gate_mode = self.query(":PULSE0:GATE:MODE").strip()
        self.check_ok()
        if global_gate_mode == "CHAN":
            channel = self.set_channel()
            logic = self.query(f":PULSE{channel}:CLOGIC").strip()
            self.check_ok()
            return logic
        else:
            logic = self.query(f":PULSE0:GATE:LOGIC").strip()
            self.check_ok()
            return logic
        
    @gate_logic.setter
    def gate_logic(self, logic):
        self.received = False
        global_gate_mode = self.query(":PULSE0:GATE:MODE").strip()
        self.check_ok()
        if global_gate_mode == "CHAN":
            channel = self.set_channel()
            self.set(f":PULSE{channel}:CLOGIC", logic)
            self.check_ok()
        else:
            self.set(f":PULSE0:GATE:LOGIC", logic)
            self.check_ok()

    @property
    def channel_gate_mode(self):
        self.received = False
        global_gate_mode = self.query(":PULSE0:GATE:MODE").strip()
        self.check_ok()
        if global_gate_mode == "CHAN":
            channel = self.set_channel()
            mode = self.query(f":PULSE{channel}:CGATE").strip()
            self.check_ok()
            return mode
        else:
            return "DIS"
        
    @channel_gate_mode.setter
    def channel_gate_mode(self, channel_gate_mode):
        self.received = False
        global_gate_mode = self.query(":PULSE0:GATE:MODE").strip()
        self.check_ok()
        channel = self.set_channel()
        if global_gate_mode == "CHAN":
            self.set(f":PULSE{channel}:CGATE", channel_gate_mode)
            self.check_ok()
        else:
            self.set(f":PULSE0:GATE:MODE", "CHAN")
            self.check_ok()
            self.set(f":PULSE{channel}:CGATE", channel_gate_mode)
            self.check_ok()

    @property
    def period(self):
        self.received = False
        period = float(self.query(":PULSE0:PER").strip())
        self.check_ok()
        return period
    
    @period.setter
    def period(self, period):
        self.received = False
        self.set(f":PULSE0:PER", str(period))
        self.check_ok()

    @property
    def delay(self):
        self.received = False
        channel = self.set_channel()
        delay = float(self.query(f":PULSE{channel}:DELAY").strip())
        self.check_ok()
        return delay

    @delay.setter
    def delay(self, delay):
        self.received = False
        channel = self.set_channel()
        self.set(f":PULSE{channel}:DELAY", "{:10.9f}".format(delay))
        self.check_ok()

    @property
    def width(self):
        self.received = False
        channel = self.set_channel()
        width = float(self.query(f":PULSE{channel}:WIDT").strip())
        self.check_ok()
        return width
    
    @width.setter
    def width(self, width):
        self.received = False
        channel = self.set_channel()
        self.set(f":PULSE{channel}:WIDT", "{:10.9f}".format(width))
        self.check_ok()

    @property
    def amplitude_mode(self):
        self.received = False
        channel = self.set_channel()
        mode = self.query(f":PULSE{channel}:OUTP:MODE").strip()
        self.check_ok()
        return mode
    
    @amplitude_mode.setter
    def amplitude_mode(self, mode):
        self.received = False
        channel = self.set_channel()
        self.set(f":PULSE{channel}:OUTP:MODE", mode)
        self.check_ok()

    @property
    def amplitude(self):
        self.received = False
        channel = self.set_channel()
        amp = float(self.query(f":PULSE{channel}:OUTP:AMPL").strip())
        self.check_ok()
        return amp
    
    @amplitude.setter
    def amplitude(self, amplitude):
        self.received = False
        amp_mode = self.amplitude_mode
        if amp_mode == "ADJ":
            channel = self.set_channel()
            self.set(f":PULSE{channel}:OUTP:AMPL", str(amplitude))
            self.check_ok()
        else:
            raise ValueError("In TTL mode. Switch to ADJ mode before setting amplitude.")

    @property
    def polarity(self):
        self.received = False
        channel = self.set_channel()
        pol = self.query(f":PULSE{channel}:POL").strip()
        self.check_ok()
        return pol
    
    @polarity.setter
    def polarity(self, pol):
        self.received = False
        channel = self.set_channel()
        self.set(f":PULSE{channel}:POL", pol)
        self.check_ok()

    def output(self):
        return [
            {
                'title': 'Connection', 'name': 'connection', 'type': 'group', 'children': [
                    {'title': 'Controller', 'name': 'id', 'type': 'str', 'value': self.idn(), 'readonly': True},
                    {'title': 'IP', 'name': 'ip', 'type': 'str', 'value': self.ip, 'default': self.ip},
                    {'title': 'Port', 'name': 'port', 'type': 'int', 'value': self.port, 'default': 2001}
                ]
            },
            {
                'title': 'Device Configuration State', 'name': 'config', 'type': 'group', 'children': [
                    {'title': 'Configuration Label', 'name': 'label', 'type': 'str', 'value': self.label},
                    {'title': 'Local Memory Slot', 'name': 'slot', 'type': 'list', 'value': self.slot, 'limits': list(range(1, 13))},
                    {'title': 'Save Current Configuration?', 'name': 'save', 'type': 'bool_push', 'label': 'Save', 'value': False},
                    {'title': 'Restore Previous Configuration?', 'name': 'restore', 'type': 'bool_push', 'label': 'Restore', 'value': False},
                    {'title': 'Reset Device?', 'name': 'reset', 'type': 'bool_push', 'label': 'Reset', 'value': False}
                ]
            },
            {
                'title': 'Device Output State', 'name': 'output', 'type': 'group', 'children': [
<<<<<<< HEAD
                    {'title': 'Global State', 'name': 'global_state', 'type': 'led_push', 'value': self.global_state, 'default': "OFF", 'limits': ['ON', 'OFF']},
                    {'title': 'Global Mode', 'name': 'global_mode', 'type': 'list', 'value': self.global_mode, 'limits': ['NORM', 'SING', 'BURS', 'DCYC']},
                    {'title': 'Channel', 'name': 'channel_label', 'type': 'list', 'value': self.channel_label, 'limits': ['A', 'B', 'C', 'D']},
                    {'title': 'Channel Mode', 'name': 'channel_mode', 'type': 'list', 'value': self.channel_mode, 'limits': ['NORM', 'SING', 'BURS', 'DCYC']},
                    {'title': 'Channel State', 'name': 'channel_state', 'type': 'led_push', 'value': self.channel_state, 'default': "OFF", 'limits': ['ON', 'OFF']},
                    {'title': 'Width (ns)', 'name': 'width', 'type': 'float', 'value': self.width * 1e9, 'default': 10, 'min': 10, 'max': 999e9},
                    {'title': 'Delay (ns)', 'name': 'delay', 'type': 'float', 'value': self.delay * 1e9, 'default': 0, 'min': 0, 'max': 999.0}
=======
                    {'title': 'Global State', 'name': 'global_state', 'type': 'led_push', 'value': await self.get_global_state(), 'default': False},
                    {'title': 'Global Mode', 'name': 'global_mode', 'type': 'list', 'value': await self.get_global_mode(), 'limits': ['NORM', 'SING', 'BURS', 'DCYC']},
                    {'title': 'Channel', 'name': 'channel_label', 'type': 'list', 'value': self.channel_label, 'limits': ['A', 'B', 'C', 'D']},
                    {'title': 'Channel Mode', 'name': 'channel_mode', 'type': 'list', 'value': await self.get_channel_mode(), 'limits': ['NORM', 'SING', 'BURS', 'DCYC']},
                    {'title': 'Channel State', 'name': 'channel_state', 'type': 'led_push', 'value': await self.get_channel_state(), 'default': False},
                    {'title': 'Width (ns)', 'name': 'width', 'type': 'float', 'value': await self.get_width() * 1e9, 'default': 10, 'min': 10, 'max': 999e9},
                    {'title': 'Delay (ns)', 'name': 'delay', 'type': 'float', 'value': await self.get_delay() * 1e9, 'default': 0, 'min': 0, 'max': 999.0}
>>>>>>> 8ef305a260ba497a0c83ba425715f5483ae532b0
                ]
            },
            {
                'title': 'Amplitude Profile', 'name': 'amp', 'type': 'group', 'children': [
                    {'title': 'Amplitude Mode', 'name': 'amplitude_mode', 'type': 'list', 'value': self.amplitude_mode, 'limits': ['ADJ', 'TTL']},
                    {'title': 'Amplitude (V)', 'name': 'amplitude', 'type': 'float', 'value': self.amplitude, 'default': 2.0, 'min': 2.0, 'max': 20.0},
                    {'title': 'Polarity', 'name': 'polarity', 'type': 'list', 'value': self.polarity, 'limits': ['NORM', 'COMP', 'INV']}
                ]
            },
            {
                'title': 'Continuous Mode', 'name': 'continuous_mode', 'type': 'group', 'children': [
                    {'title': 'Period (s)', 'name': 'period', 'type': 'float', 'value': self.period, 'default': 1e-3, 'min': 100e-9, 'max': 5000.0},
                    {'title': 'Repetition Rate (Hz)', 'name': 'rep_rate', 'type': 'float', 'value': 1.0 / self.period, 'default': 1e3, 'min': 2e-4, 'max': 10e6}
                ]
            },
            {
                'title': 'Trigger Mode', 'name': 'trigger_mode', 'type': 'group', 'children': [
                    {'title': 'Trigger Mode', 'name': 'trig_mode', 'type': 'list', 'value': self.trig_mode, 'limits': ['DIS', 'TRIG']},
                    {'title': 'Trigger Threshold (V)', 'name': 'trig_thresh', 'type': 'float', 'value': self.trig_thresh, 'default': 2.5, 'min': 0.2, 'max': 15.0},
                    {'title': 'Trigger Edge', 'name': 'trig_edge', 'type': 'list', 'value': self.trig_edge, 'limits': ['RISING', 'FALLING']}
                ]
            },
            {
                'title': 'Gating', 'name': 'gating', 'type': 'group', 'children': [
                    {'title': 'Global Gate Mode', 'name': 'gate_mode', 'type': 'list', 'value': self.gate_mode, 'limits': ['DIS', 'PULS', 'OUTP', 'CHAN']},
                    {'title': 'Channel Gate Mode', 'name': 'channel_gate_mode', 'type': 'list', 'value': self.channel_gate_mode, 'limits': ['DIS', 'PULS', 'OUTP']},
                    {'title': 'Gate Threshold (V)', 'name': 'gate_thresh', 'type': 'float', 'value': self.gate_thresh, 'default': 2.5, 'min': 0.2, 'max': 15.0},
                    {'title': 'Gate Logic', 'name': 'gate_logic', 'type': 'list', 'value': self.gate_logic, 'limits': ['HIGH', 'LOW']}
                ]
            }
        ]

