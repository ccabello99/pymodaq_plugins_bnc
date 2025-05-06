import time
from pymodaq_plugins_bnc.hardware.device import Device
from qtpy.QtCore import QThread

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
            QThread.msleep(20)
            if time.time() - start > 3:  # 3-second timeout
                print("Timeout waiting for device response")
                return ''
        self.received = False

    def idn(self):
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
        self.set("*SAV", str(self.slot))
        self.check_ok()
    
    def restore_state(self):
        self.set("*RCL", str(self.slot))
        self.check_ok()
    
    def trig(self):
        self.send("*TRG")
        self.check_ok()
    
    @property
    def label(self):
        lbl = self.query("*LBL").strip()
        self.check_ok()
        return lbl
    
    @label.setter
    def label(self, label):
        self.set("*LBL", "\"" + label + "\"")
        self.check_ok()
        
    @property
    def global_state(self):
        state = self.query(":INST:STATE").strip()
        self.check_ok()
        return True if state == "1" else False

    @global_state.setter
    def global_state(self, state):
        self.set(":INST:STATE", state)
        self.check_ok()
    
    @property
    def global_mode(self):
        mode = self.query(":PULSE0:MODE")
        self.check_ok()
        return mode
    
    @global_mode.setter
    def global_mode(self, mode):
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
        channel = self.set_channel()
        mode = self.query(f":PULSE{channel}:CMOD").strip()
        self.check_ok()
        return mode

    @channel_mode.setter
    def channel_mode(self, mode):
        channel = self.set_channel()
        self.set(f":PULSE{channel}:CMOD", mode)
        self.check_ok()
        
    @property
    def channel_state(self):
        channel = self.set_channel()
        state = self.query(f":PULSE{channel}:STATE").strip()
        self.check_ok()
        return True if state == "1" else False

    @channel_state.setter    
    def channel_state(self, state):
        channel = self.set_channel()
        self.set(f":PULSE{channel}:STATE", state)
        self.check_ok()

    @property
    def trig_mode(self):
        trig_mode = self.query(":PULSE0:TRIG:MODE").strip()
        self.check_ok()
        return trig_mode

    @trig_mode.setter
    def trig_mode(self, mode):
        self.set(f":PULSE0:TRIG:MODE", mode)
        self.check_ok()
        
    @property        
    def trig_thresh(self):
        thresh = float(self.query(":PULSE0:TRIG:LEV").strip())
        self.check_ok()
        return thresh
    
    @trig_thresh.setter
    def trig_thresh(self, thresh):
        self.set(f":PULSE0:TRIG:LEV", str(thresh))
        self.check_ok()

    @property
    def trig_edge(self):
        edge = self.query(":PULSE0:TRIG:EDGE").strip()
        self.check_ok()
        return edge
    
    @trig_edge.setter
    def trig_edge(self, edge):
        self.set(f":PULSE0:TRIG:EDGE", edge)
        self.check_ok()

    @property
    def gate_mode(self):
        gate_mode = self.query(":PULSE0:GATE:MODE").strip()
        self.check_ok()
        return gate_mode

    @gate_mode.setter
    def gate_mode(self, mode):
        self.set(f":PULSE0:GATE:MODE", mode)
        self.check_ok()

    @property        
    def gate_thresh(self):
        thresh = float(self.query(":PULSE0:GATE:LEV").strip())
        self.check_ok()
        return thresh
    
    @gate_thresh.setter
    def gate_thresh(self, thresh):
        self.set(f":PULSE0:GATE:LEV", str(thresh))
        self.check_ok()

    @property
    def gate_logic(self):
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
        period = float(self.query(":PULSE0:PER").strip())
        self.check_ok()
        return period
    
    @period.setter
    def period(self, period):
        self.set(f":PULSE0:PER", str(period))
        self.check_ok()

    @property
    def delay(self):
        channel = self.set_channel()
        delay = float(self.query(f":PULSE{channel}:DELAY").strip())
        self.check_ok()
        return delay

    @delay.setter
    def delay(self, delay):
        channel = self.set_channel()
        self.set(f":PULSE{channel}:DELAY", "{:10.9f}".format(delay))
        self.check_ok()

    @property
    def width(self):
        channel = self.set_channel()
        width = float(self.query(f":PULSE{channel}:WIDT").strip())
        self.check_ok()
        return width
    
    @width.setter
    def width(self, width):
        channel = self.set_channel()
        self.set(f":PULSE{channel}:WIDT", "{:10.9f}".format(width))
        self.check_ok()

    @property
    def amplitude_mode(self):
        channel = self.set_channel()
        mode = self.query(f":PULSE{channel}:OUTP:MODE").strip()
        self.check_ok()
        return mode
    
    @amplitude_mode.setter
    def amplitude_mode(self, mode):
        channel = self.set_channel()
        self.set(f":PULSE{channel}:OUTP:MODE", mode)
        self.check_ok()

    @property
    def amplitude(self):
        channel = self.set_channel()
        amp = float(self.query(f":PULSE{channel}:OUTP:AMPL").strip())
        self.check_ok()
        return amp
    
    @amplitude.setter
    def amplitude(self, amplitude):
        amp_mode = self.amplitude_mode
        if amp_mode == "ADJ":
            channel = self.set_channel()
            self.set(f":PULSE{channel}:OUTP:AMPL", str(amplitude))
            self.check_ok()
        else:
            raise ValueError("In TTL mode. Switch to ADJ mode before setting amplitude.")

    @property
    def polarity(self):
        channel = self.set_channel()
        pol = self.query(f":PULSE{channel}:POL").strip()
        self.check_ok()
        return pol
    
    @polarity.setter
    def polarity(self, pol):
        channel = self.set_channel()
        self.set(f":PULSE{channel}:POL", pol)
        self.check_ok()

    def output(self):
        return [
            {
                'title': 'Connection', 'name': 'connection', 'type': 'group', 'children': [
                    {'title': 'Controller', 'name': 'id', 'type': 'str', 'value': self.idn(), 'readonly': True},
                    {'title': 'IP', 'name': 'ip', 'type': 'str', 'value': self.ip, 'default': self.ip},
                    {'title': 'Port', 'name': 'port', 'type': 'int', 'value': self.port, 'default': 2001},
                    {'title': 'Still Communicating ?', 'name': 'still_com', 'type': 'led', 'value': self.still_communicating}
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
                    {'title': 'Global State', 'name': 'global_state', 'type': 'led_push', 'value': self.global_state},
                    {'title': 'Global Mode', 'name': 'global_mode', 'type': 'list', 'value': self.global_mode, 'limits': ['NORM', 'SING', 'BURS', 'DCYC']},
                    {'title': 'Channel', 'name': 'channel_label', 'type': 'list', 'value': self.channel_label, 'limits': ['A', 'B', 'C', 'D']},
                    {'title': 'Channel Mode', 'name': 'channel_mode', 'type': 'list', 'value': self.channel_mode, 'limits': ['NORM', 'SING', 'BURS', 'DCYC']},
                    {'title': 'Channel State', 'name': 'channel_state', 'type': 'led_push', 'value': self.channel_state},
                    {'title': 'Width (ns)', 'name': 'width', 'type': 'float', 'value': self.width * 1e9, 'default': 10, 'min': 10, 'max': 999e9},
                    {'title': 'Delay (ns)', 'name': 'delay', 'type': 'float', 'value': self.delay * 1e9, 'default': 0, 'min': 0, 'max': 999.0}
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
                    {'title': 'Trigger Edge', 'name': 'trig_edge', 'type': 'list', 'value': self.trig_edge, 'limits': ['RIS', 'FALL']}
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

