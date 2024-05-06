import time
from pymodaq_plugins_bnc.hardware.device import Device

class BNC575(Device):

    def __init__(self, ip, port):
        super().__init__(ip, port)
        self.channel_label = "A"
        self.slot = 1

    def idn(self):
        idn = self.query("*IDN").strip()
        time.sleep(0.25)
        return idn

    @property
    def ip(self):
        return self.ip

    @property
    def port(self):
        return self.port

    def reset(self):
        self.send("*RST")
        time.sleep(0.05)

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
        time.sleep(0.05)
    
    def restore_state(self):
        self.set("*RCL", str(self.slot))
        time.sleep(0.05)
    
    def trig(self):
        self.send("*TRG")
        time.sleep(0.05)
    
    @property
    def label(self):
        lbl = self.query("*LBL").strip()
        time.sleep(0.05)
        return lbl
    
    @label.setter
    def label(self, label):
        self.set("*LBL", "\"" + label + "\"")
        time.sleep(0.05)
        
    @property
    def global_state(self):
        state = self.query(":INST:STATE").strip()
        time.sleep(0.05)
        if state == "1":
            return "ON"
        else:
            return "OFF"

    @global_state.setter
    def global_state(self, state):
        if state == "ON":
            self.set(":INST:STATE", "ON")
        else:
            self.set(":INST:STATE", "OFF")
        time.sleep(0.05)
    
    @property
    def global_mode(self):
        mode = self.query(":PULSE0:MODE")
        time.sleep(0.05)
        return mode
    
    @global_mode.setter
    def global_mode(self, mode):
        self.set(":PULSE0:MODE", mode)
        time.sleep(0.05)
        
    def close(self):
        self.com.close()
    
    def set_channel(self):
        if self.channel_label == "A":
            channel = 1
            return channel
        elif self.channel_label == "B":
            channel = 2
            return channel
        elif self.channel_label == "C":
            channel = 3
            return channel
        elif self.channel_label == "D":
            channel = 4
            return channel

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
        time.sleep(0.05)
        return mode

    @channel_mode.setter
    def channel_mode(self, mode):
        channel = self.set_channel()
        self.set(f":PULSE{channel}:CMOD", mode)
        time.sleep(0.05)
        
    @property
    def channel_state(self):
        channel = self.set_channel()
        state = self.query(f":PULSE{channel}:STATE").strip()
        time.sleep(0.05)
        if state == "1":
            return "ON"
        else:
            return "OFF"

    @channel_state.setter    
    def channel_state(self, state):
        channel = self.set_channel()
        self.set(f":PULSE{channel}:STATE", state)
        time.sleep(0.05)

    @property
    def trig_mode(self):
        trig_mode = self.query(":PULSE0:TRIG:MODE").strip()
        time.sleep(0.05)
        return trig_mode

    @trig_mode.setter
    def trig_mode(self, mode):
        self.set(f":PULSE0:TRIG:MODE", mode)
        time.sleep(0.05)
        
    @property        
    def trig_thresh(self):
        thresh = float(self.query(":PULSE0:TRIG:LEV").strip())
        time.sleep(0.05)
        return thresh
    
    @trig_thresh.setter
    def trig_thresh(self, thresh):
        self.set(f":PULSE0:TRIG:LEV", str(thresh))
        time.sleep(0.05)

    @property
    def trig_edge(self):
        edge = self.query(":PULSE0:TRIG:EDGE").strip()
        time.sleep(0.05)
        if edge == "RIS":
            return "RISING"
        else:
            return "FALLING"
    
    @trig_edge.setter
    def trig_edge(self, edge):
        self.set(f":PULSE0:TRIG:EDGE", edge)
        time.sleep(0.05)

    @property
    def gate_mode(self):
        gate_mode = self.query(":PULSE0:GATE:MODE").strip()
        time.sleep(0.05)
        return gate_mode

    @gate_mode.setter
    def gate_mode(self, mode):
        self.set(f":PULSE0:GATE:MODE", mode)

    @property        
    def gate_thresh(self):
        thresh = float(self.query(":PULSE0:GATE:LEV").strip())
        time.sleep(0.05)
        return thresh
    
    @gate_thresh.setter
    def gate_thresh(self, thresh):
        self.set(f":PULSE0:GATE:LEV", str(thresh))
        time.sleep(0.05)

    @property
    def gate_logic(self):
        global_gate_mode = self.query(":PULSE0:GATE:MODE").strip()
        time.sleep(0.05)
        if global_gate_mode == "CHAN":
            channel = self.set_channel()
            logic = self.query(f":PULSE{channel}:CLOGIC").strip()
            time.sleep(0.05)
            return logic
        else:
            logic = self.query(f":PULSE0:GATE:LOGIC").strip()
            time.sleep(0.05)
            return logic
        
    @gate_logic.setter
    def gate_logic(self, logic):
        global_gate_mode = self.query(":PULSE0:GATE:MODE").strip()
        time.sleep(0.05)
        if global_gate_mode == "CHAN":
            channel = self.set_channel()
            self.set(f":PULSE{channel}:CLOGIC", logic)
            time.sleep(0.05)
        else:
            self.set(f":PULSE0:GATE:LOGIC", logic)
            time.sleep(0.05)

    @property
    def channel_gate_mode(self):
        global_gate_mode = self.query(":PULSE0:GATE:MODE").strip()
        time.sleep(0.05)
        if global_gate_mode == "CHAN":
            channel = self.set_channel()
            mode = self.query(f":PULSE{channel}:CGATE").strip()
            time.sleep(0.05)
            return mode
        else:
            return "DIS"
        
    @channel_gate_mode.setter
    def channel_gate_mode(self, channel_gate_mode):
        global_gate_mode = self.query(":PULSE0:GATE:MODE").strip()
        channel = self.set_channel()
        time.sleep(0.05)
        if global_gate_mode == "CHAN":
            channel = self.set_channel()
            self.set(f":PULSE{channel}:CGATE", channel_gate_mode)
            time.sleep(0.05)
        else:
            self.set(f":PULSE0:GATE:MODE", "CHAN")
            time.sleep(0.05)
            self.set(f":PULSE{channel}:CGATE", channel_gate_mode)
            time.sleep(0.05)

    @property
    def period(self):
        period = float(self.query(":PULSE0:PER").strip())
        time.sleep(0.05)
        return period
    
    @period.setter
    def period(self, period):
        self.set(f":PULSE0:PER", str(period))
        time.sleep(0.05)

    @property
    def delay(self):
        channel = self.set_channel()
        delay = float(self.query(f":PULSE{channel}:DELAY").strip())
        time.sleep(0.05)
        return delay

    @delay.setter
    def delay(self, delay):
        channel = self.set_channel()
        self.set(f":PULSE{channel}:DELAY", "{:10.9f}".format(delay))
        time.sleep(0.05)

    @property
    def width(self):
        channel = self.set_channel()
        width = float(self.query(f":PULSE{channel}:WIDT").strip())
        time.sleep(0.05)
        return width
    
    @width.setter
    def width(self, width):
        channel = self.set_channel()
        self.set(f":PULSE{channel}:WIDT", "{:10.9f}".format(width))
        time.sleep(0.05)

    @property
    def amplitude_mode(self):
        channel = self.set_channel()
        mode = self.query(f":PULSE{channel}:OUTP:MODE").strip()
        time.sleep(0.05)
        return mode
    
    @amplitude_mode.setter
    def amplitude_mode(self, mode):
        channel = self.set_channel()
        self.set(f":PULSE{channel}:OUTP:MODE", mode)
        time.sleep(0.05)

    @property
    def amplitude(self):
        channel = self.set_channel()
        amp = float(self.query(f":PULSE{channel}:OUTP:AMPL").strip())
        time.sleep(0.05)
        return amp
    
    @amplitude.setter
    def amplitude(self, amplitude):
        amp_mode = self.amplitude_mode
        if amp_mode == "ADJ":
            channel = self.set_channel()
            self.set(f":PULSE{channel}:OUTP:AMPL", str(amplitude))
            time.sleep(0.05)
        else:
            return "In TTL mode. First, switch to ADJ mode."

    @property
    def polarity(self):
        channel = self.set_channel()
        pol = self.query(f":PULSE{channel}:POL").strip()
        time.sleep(0.05)
        return pol
    
    @polarity.setter
    def polarity(self, pol):
        channel = self.set_channel()
        self.set(f":PULSE{channel}:POL", pol)
        time.sleep(0.05)

    def output(self):
        out = {}
        out['IP Address'] = self.ip
        time.sleep(0.075)
        out['Port'] = self.port
        time.sleep(0.075)
        out['Configuration Label'] = self.label
        time.sleep(0.075)
        out['Local Memory Slot'] = self.slot
        time.sleep(0.075)
        out['Global State'] = self.global_state
        time.sleep(0.075)
        out['Global Mode'] = self.global_mode
        time.sleep(0.075)
        out['Channel'] = self.channel_label
        time.sleep(0.075)
        out['Channel Mode'] = self.channel_mode
        time.sleep(0.075)
        out['Channel State'] = self.channel_state
        time.sleep(0.075)
        out['Width (s)'] = self.width
        time.sleep(0.075)
        out['Amplitude Mode'] = self.amplitude_mode
        time.sleep(0.075)
        out['Amplitude (V)'] = self.amplitude
        time.sleep(0.075)
        out['Polarity'] = self.polarity
        time.sleep(0.075)
        out['Delay (s)'] = self.delay
        time.sleep(0.075)
        out['Period (s)'] = self.period
        time.sleep(0.075)
        out['Trigger Mode'] = self.trig_mode
        time.sleep(0.075)
        out['Trigger Threshold (V)'] = self.trig_thresh
        time.sleep(0.075)
        out['Trigger Edge'] = self.trig_edge
        time.sleep(0.075)
        out['Global Gate Mode'] = self.gate_mode
        time.sleep(0.075)
        out['Channel Gate Mode'] = self.channel_gate_mode
        time.sleep(0.075)
        out['Gate Threshold (V)'] = self.gate_thresh
        time.sleep(0.075)
        out['Gate Logic'] = self.gate_logic
        time.sleep(0.075)

        return out
        
