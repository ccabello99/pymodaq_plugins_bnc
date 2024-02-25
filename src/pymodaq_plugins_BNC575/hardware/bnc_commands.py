import time
import numpy as np
from pymodaq_plugins_BNC575.hardware.device import Device

class BNC575(Device):

    def __init__(self, ip, port):
        super().__init__(ip, port)
        self.channel = np.array([1,2,3,4])

    def idn(self):
        idn = self.query("*IDN").strip()
        time.sleep(0.05)
        return idn
    
    def restore_state(self,slot):
        self.set("*RCL", str(slot))
        time.sleep(0.05)
    
    def reset(self):
        self.send("*RST")
        time.sleep(0.05)
    
    def save_state(self,slot):
        self.set("*SAV", str(slot))
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
        
    def arm(self):
        self.set(":INST:STATE", "ON")
        time.sleep(0.05)
    
    def close(self):
        self.com.close()

    def set_channel(self, channel_label):
        if channel_label == "A":
            channel = self.channel[0]
            return channel
        elif channel_label == "B":
            channel = self.channel[1]
            return channel
        elif channel_label == "C":
            channel = self.channel[2]
            return channel
        elif channel_label == "D":
            channel = self.channel[3]
            return channel
        
    @property
    def channel_mode(self, channel_label):
        channel = self.set_channel(channel_label)
        mode = self.query(f":PULSE{channel}:CMOD").strip()
        time.sleep(0.05)
        return mode

    @channel_mode.setter
    def channel_mode(self, channel_label, mode):
        channel = self.set_channel(channel_label)
        if mode == "NORM" or "SING" or "BURS" or "DCYC":
            self.set(f":PULSE{channel}:CMOD", mode)
            time.sleep(0.05)
        else:
            raise ValueError("Invalid mode input. Try \"NORM\", \"SING\", \"BURS\", or \"DCYC\"")
        
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
            return "Triggered from Rising Edge"
        else:
            return "Triggered from Falling Edge"
    
    @trig_edge.setter
    def trig_edge(self, rising):
        EDGE = "RIS" if rising else "FALL"
        self.set(f":PULSE0:TRIG:EDGE", EDGE)
        time.sleep(0.05)

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
    def gate_logic(self, channel_label):
        global_gate_mode = self.query(":PULSE0:GATE:MODE").strip()
        time.sleep(0.05)
        if global_gate_mode == "CHAN":
            channel = self.set_channel(channel_label)
            logic = self.query(f":PULSE{channel}:CLOGIC").strip()
            time.sleep(0.05)
            return "Active High" if logic == "HIGH" else "Active Low"
        else:
            logic = self.query(f":PULSE0:LOGIC").strip()
            time.sleep(0.05)
            return "Active High" if logic == "HIGH" else "Active Low"
        
    @gate_logic.setter
    def gate_logic(self, channel_label, high):
        global_gate_mode = self.query(":PULSE0:GATE:MODE").strip()
        time.sleep(0.05)
        EDGE = "HIGH" if high else "LOW"
        if global_gate_mode == "CHAN":
            channel = self.set_channel(channel_label)
            self.set(f":PULSE{channel}:CLOGIC", EDGE)
            time.sleep(0.05)
        else:
            self.set(f":PULSE0:LOGIC", EDGE)
            time.sleep(0.05)

    @property
    def channel_gate_mode(self, channel_label):
        global_gate_mode = self.query(":PULSE0:GATE:MODE").strip()
        time.sleep(0.05)
        if global_gate_mode == "CHAN":
            channel = self.set_channel(channel_label)
            mode = self.query(f":PULSE{channel}:CGATE").strip()
            time.sleep(0.05)
            return mode
        else:
            return global_gate_mode
        
    @channel_gate_mode.setter
    def channel_gate_mode(self, channel_label, channel_gate_mode):
        global_gate_mode = self.query(":PULSE0:GATE:MODE").strip()
        time.sleep(0.05)
        if global_gate_mode == "CHAN":
            channel = self.set_channel(channel_label)
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
    def delay(self, channel_label):
        channel = self.set_channel(channel_label)
        delay = float(self.query(f":PULSE{channel}:DELAY").strip())
        time.sleep(0.05)
        return delay

    @delay.setter
    def delay(self, channel_label, delay):
        channel = self.set_channel(channel_label)
        self.set(f":PULSE{channel}:DELAY", "{:10.9f}".format(delay))
        time.sleep(0.05)

    @property
    def width(self, channel_label):
        channel = self.set_channel(channel_label)
        width = float(self.query(f":PULSE{channel}:WIDT").strip())
        time.sleep(0.05)
        return width
    
    @width.setter
    def width(self, channel_label, width):
        channel = self.set_channel(channel_label)
        self.set(f":PULSE{channel}:WIDT", "{:10.9f}".format(width))
        time.sleep(0.05)

    @property
    def amplitude(self, channel_label):
        channel = self.set_channel(channel_label)
        amp = float(self.query(f":PULSE{channel}:OUTP:AMPL").strip())
        time.sleep(0.05)
        return amp
    
    @amplitude.setter
    def amplitude(self, channel_label, amplitude):
        channel = self.set_channel(channel_label)
        self.set(f":PULSE{channel}:OUTP:AMPL", str(amplitude))
        time.sleep(0.05)

    @property
    def state(self, channel_label):
        channel = self.set_channel(channel_label)
        state = self.query(f":PULSE{channel}:STATE").strip()
        time.sleep(0.05)
        return state

    @state.setter    
    def state(self, channel_label, state):
        channel = self.set_channel(channel_label)
        if state == "ON" or "on":
            self.set(f":PULSE{channel}:STATE", "ON")
        elif state == "OFF" or "off":
            self.set(f":PULSE{channel}:STATE", "OFF")
        else:
            raise ValueError("Invalid state input. Try \"ON\" or \"OFF\"")
        time.sleep(0.05)
        
    def set_periodic(self):
        self.set(f":PULSE0:MODE", "NORM")
        time.sleep(0.05)

    @property
    def trig_mode(self):
        trig_mode = self.query(":PULSE0:TRIG:MODE").strip()
        if trig_mode == "TRIG":
            return "Yes"
        elif trig_mode == "DIS":
            return "No"
        else:
            raise IOError("Wrong return from device")

    @trig_mode.setter
    def trig_mode(self, mode):
        if mode == "TRIG" or "trig":
            self.set(f":PULSE0:TRIG:MODE", "TRIG")
            time.sleep(0.05)
        elif mode == "DIS" or "dis":
            self.set(f":PULSE0:TRIG:MODE", "DIS")
            time.sleep(0.05)
        else:
            raise ValueError("Invalid input. Try \"TRIG\" or \"DIS\"")

    def output(self, channel_label):
        out = {}
        out['Channel'] = channel_label
        mode = self.channel_mode(channel_label)
        if mode == "NORM":
            out['State'] = self.state(channel_label)
            out['Continuous Mode'] = "Yes"
            out['Amplitude (V)'] = self.amplitude(channel_label)
            out['Period (s)'] = self.period(channel_label)
            out['Pulse Width (s)'] = self.width(channel_label)
            out['Pulse Delay (s)'] = self.delay(channel_label)
            
        elif mode == "SING":
            out['State'] = self.state(channel_label)
            out['Trigger Mode'] = self.trigger_mode()
            out['Trigger Threshold'] = self.trig_thresh(channel_label)
            out['Trigger Edge'] = self.trig_edge(channel_label)
            out['Amplitude (V)'] = self.amplitude(channel_label)
            out['Pulse Width (s)'] = self.width(channel_label)
            out['Pulse Delay (s)'] = self.delay(channel_label)
                

        gate_mode = self.query(":PULSE0:GATE:MODE").strip()
        if gate_mode == "DIS":
            out['Gating Active'] = "No"
            out['Gate Threshold (V)'] = self.gate_thresh(channel_label)
            out['Gate Logic'] = self.gate_logic(channel_label)
        elif gate_mode == "CHAN":
            out['Gating Active'] = "Yes"
            out['Channel Gate Mode'] = self.channel_gate_mode(channel_label)
            out['Gate Threshold (V)'] = self.gate_thresh(channel_label)
            out['Gate Logic'] = self.gate_logic(channel_label)
        elif gate_mode == "PULS":
            out['Gating Active'] = "Yes"
            out['Gate Mode'] = gate_mode
            out['Gate Threshold (V)'] = self.gate_thresh(channel_label)
            out['Gate Logic'] = self.gate_logic(channel_label)
        elif gate_mode == "OUTP":
            out['Gating Active'] = "Yes"
            out['Gate Mode'] = gate_mode
            out['Gate Threshold (V)'] = self.gate_thresh(channel_label)
            out['Gate Logic'] = self.gate_logic(channel_label)

        return out

                

        
