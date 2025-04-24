from pymodaq.control_modules.move_utility_classes import DAQ_Move_base, comon_parameters_fun, main, DataActuatorType,\
    DataActuator  # common set of parameters for all actuators
from pymodaq.utils.daq_utils import ThreadCommand # object used to send info back to the main thread
from pymodaq.utils.parameter import Parameter
from pymodaq_plugins_bnc.hardware.bnc_commands import BNC575
import time


class DAQ_Move_bnc(DAQ_Move_base):
    """ Instrument plugin class for an actuator.
    
    This object inherits all functionalities to communicate with PyMoDAQ’s DAQ_Move module through inheritance via
    DAQ_Move_base. It makes a bridge between the DAQ_Move module and the Python wrapper of a particular instrument.

        * This is compatible with the BNC 575 Delay/Pulse Generator
        * Tested on PyMoDAQ 4.1.1
        * Tested on Python 3.8.18
        * No additional drivers necessary

    Attributes:
    -----------
    controller: object
        The particular object that allow the communication with the hardware, in general a python wrapper around the
         hardware library.

    """
    _controller_units = 'ns'
    is_multiaxes = False
    _axis_names = ['Delay']
    #data_actuator_type = DataActuatorType['DataActuator']  # wether you use the new data style for actuator otherwise set this
    # as  DataActuatorType['float']  (or entirely remove the line)

    params = [
    {'title': 'Connection', 'name': 'connection', 'type': 'group', 'children': [
        {'title': 'Controller', 'name': 'id', 'type': 'str', 'value': 'BNC,575-4,31309,2.4.1-1.2.2', 'readonly': True},
        {'title': 'IP', 'name': 'ip', 'type': 'str', 'value': ''},
        {'title': 'Port', 'name': 'port', 'type': 'str', 'value': ''}
    ]},

    {'title': 'Device Configuration State', 'name': 'config', 'type': 'group', 'children': [
        {'title': 'Configuration Label', 'name': 'label', 'type': 'str', 'value': ""},
        {'title': 'Local Memory Slot', 'name': 'slot', 'type': 'list', 'value': 1, 'limits': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]},
        {'title': 'Save Current Configuration?', 'name': 'save', 'type': 'bool_push', 'label': 'Save', 'value': False},
        {'title': 'Restore Previous Configuration?', 'name': 'restore', 'type': 'bool_push', 'label': 'Restore', 'value': False},
        {'title': 'Reset Device?', 'name': 'reset', 'type': 'bool_push', 'label': 'Reset', 'value': False}
    ]},

    {'title': 'Device Output State', 'name': 'output', 'type': 'group', 'children': [
        {'title': 'Global State', 'name': 'global_state', 'type': 'led_push', 'value': "OFF", 'limits': ['ON', 'OFF']},
        {'title': 'Global Mode', 'name': 'global_mode', 'type': 'list', 'value': 'NORM', 'limits': ['NORM', 'SING', 'BURS', 'DCYC']},
        {'title': 'Channel', 'name': 'channel_label', 'type': 'list', 'value': "A", 'limits': ['A', 'B', 'C', 'D']},
        {'title': 'Channel Mode', 'name': 'channel_mode', 'type': 'list', 'value': 'NORM', 'limits': ['NORM', 'SING', 'BURS', 'DCYC']},
        {'title': 'Channel State', 'name': 'channel_state', 'type': 'led_push', 'value': "OFF", 'limits': ['ON', 'OFF']},
        {'title': 'Width (ns)', 'name': 'width', 'type': 'float', 'value': 10, 'default': 10, 'min': 10, 'max': 999e9},
        {'title': 'Amplitude Mode', 'name': 'amplitude_mode', 'type': 'list', 'value': "ADJ", 'limits': ['ADJ', 'TTL']},
        {'title': 'Amplitude (V)', 'name': 'amplitude', 'type': 'float', 'value': 2.0, 'default': 2.0, 'min': 2.0, 'max': 20.0},
        {'title': 'Polarity', 'name': 'polarity', 'type': 'list', 'value': "NORM", 'limits': ['NORM', 'COMP', 'INV']},
        {'title': 'Delay (ns)', 'name': 'delay', 'type': 'float', 'value': 0, 'default': 0, 'min': 0, 'max': 999.0},
    ]},

    {'title': 'Continuous Mode', 'name': 'continuous_mode', 'type': 'group', 'children': [
        {'title': 'Period (s)', 'name': 'period', 'type': 'float', 'value': 1e-3, 'default': 1e-3, 'min': 100e-9, 'max': 5000.0},
        {'title': 'Repetition Rate (Hz)', 'name': 'rep_rate', 'type': 'float', 'value': 1e3, 'default': 1e3, 'min': 2e-4, 'max': 10e6}
    ]},

    {'title': 'Trigger Mode', 'name': 'trigger_mode', 'type': 'group', 'children': [
        {'title': 'Trigger Mode', 'name': 'trig_mode', 'type': 'list', 'value': 'DIS', 'limits': ['DIS', 'TRIG']},
        {'title': 'Trigger Threshold (V)', 'name': 'trig_thresh', 'type': 'float', 'value': 2.5, 'default': 2.5, 'min': 0.2, 'max': 15.0},
        {'title': 'Trigger Edge', 'name': 'trig_edge', 'type': 'list', 'value': 'HIGH', 'limits': ['HIGH', 'LOW']}
    ]},

    {'title': 'Gating', 'name': 'gating', 'type': 'group', 'children': [
        {'title': 'Global Gate Mode', 'name': 'gate_mode', 'type': 'list', 'value': "DIS", 'limits': ['DIS', 'PULS', 'OUTP', 'CHAN']},
        {'title': 'Channel Gate Mode', 'name': 'channel_gate_mode', 'type': 'list', 'value': "DIS", 'limits': ['DIS', 'PULS', 'OUTP']},
        {'title': 'Gate Threshold (V)', 'name': 'gate_thresh', 'type': 'float', 'value': 2.5, 'default': 2.5, 'min': 0.2, 'max': 15.0},
        {'title': 'Gate Logic', 'name': 'gate_logic', 'type': 'list', 'value': 'HIGH', 'limits': ['HIGH', 'LOW']}

    ]}]
    # _epsilon is the initial default value for the epsilon parameter allowing pymodaq to know if the controller reached
    # the target value. It is the developer responsibility to put here a meaningful value

    def ini_attributes(self):
        self.controller: BNC575 = None

    def get_actuator_value(self):
        """Get the current value from the hardware with scaling conversion.

        Returns
        -------
        float: The delay obtained after scaling conversion.
        """
        delay = DataActuator(data=self.controller.delay*1e9)
        self.current_value = delay
        return delay

    def close(self):
        """Terminate the communication protocol"""
        self.controller.close()

    def get_config(self):
        """Start a grab from the detector"""
        
        data_dict = self.controller.output()
        
        self.settings.child('connection',  'ip').setValue(data_dict['IP Address'])
        time.sleep(0.075)
        self.settings.child('connection',  'port').setValue(data_dict['Port'])
        time.sleep(0.075)
        self.settings.child('config',  'label').setValue(data_dict['Configuration Label'])
        time.sleep(0.075)
        self.settings.child('output', 'global_state').setValue(data_dict['Global State'])
        time.sleep(0.075)
        self.settings.child('output', 'global_mode').setValue(data_dict['Global Mode'])
        time.sleep(0.075)
        self.settings.child('output', 'channel_label').setValue(data_dict['Channel'])
        time.sleep(0.075)
        self.settings.child('output', 'channel_mode').setValue(data_dict['Channel Mode'])
        time.sleep(0.075)
        self.settings.child('output', 'channel_state').setValue(data_dict['Channel State'])
        time.sleep(0.075)
        self.settings.child('output', 'width').setValue(data_dict['Width (s)'])
        time.sleep(0.075)
        self.settings.child('output', 'amplitude_mode').setValue(data_dict['Amplitude Mode'])
        time.sleep(0.075)
        self.settings.child('output', 'amplitude').setValue(data_dict['Amplitude (V)'])
        time.sleep(0.075)
        self.settings.child('output', 'polarity').setValue(data_dict['Polarity'])
        time.sleep(0.075)
        self.settings.child('output', 'delay').setValue(data_dict['Delay (s)'])
        time.sleep(0.075)
        self.get_actuator_value()
        self.settings.child('continuous_mode',  'period').setValue(data_dict['Period (s)'])
        time.sleep(0.075)
        self.settings.child('continuous_mode',  'rep_rate').setValue(1 / data_dict['Period (s)'])
        time.sleep(0.075)
        self.settings.child('trigger_mode',  'trig_mode').setValue(data_dict['Trigger Mode'])
        time.sleep(0.075)
        self.settings.child('trigger_mode',  'trig_thresh').setValue(data_dict['Trigger Threshold (V)'])
        time.sleep(0.075)
        self.settings.child('trigger_mode',  'trig_edge').setValue(data_dict['Trigger Edge'])
        time.sleep(0.075)
        self.settings.child('gating',  'gate_mode').setValue(data_dict['Global Gate Mode'])
        time.sleep(0.075)
        self.settings.child('gating',  'channel_gate_mode').setValue(data_dict['Channel Gate Mode'])
        time.sleep(0.075)
        self.settings.child('gating',  'gate_thresh').setValue(data_dict['Gate Threshold (V)'])
        time.sleep(0.075)
        self.settings.child('gating',  'gate_logic').setValue(data_dict['Gate Logic'])
        time.sleep(0.075)


    def commit_settings(self, param: Parameter):
        """Apply the consequences of a change of value in the detector settings

        Parameters
        ----------
        param: Parameter
            A given parameter (within detector_settings) whose value has been changed by the user
        """
        if param.name() == "ip":
            port = self.controller.port
            self.close()
            time.sleep(0.05)
            self.controller = self.ini_stage_init(old_controller=None,
                                              new_controller=BNC575(param.value(), port))
            time.sleep(0.05)
        if param.name() == "port":
            ip = self.controller.ip
            self.close()
            time.sleep(0.05)
            self.controller = self.ini_stage_init(old_controller=None,
                                              new_controller=BNC575(ip, param.value()))
            time.sleep(0.05)
        elif param.name() == "label":
            self.controller.label = param.value()
        elif param.name() == "slot":
           self.controller.slot = param.value()
        elif param.name() == "save":
            if param.value:
                self.controller.save_state()
                time.sleep(0.05)
        elif param.name() == "restore":
            if param.value:
                self.controller.restore_state()
                time.sleep(0.05)
                self.grab_data()
        elif param.name() == "reset":
            if param.value:
                self.controller.reset()
                time.sleep(0.05)
                self.grab_data()
        elif param.name() == "global_state":
            self.controller.global_state = param.value()
        elif param.name() == "global_mode":
            self.controller.global_mode = param.value()
        elif param.name() == "channel_label":
           self.controller.channel_label = param.value()
           self.grab_data()
        elif param.name() == "channel_state":
            self.controller.channel_state = param.value()
        elif param.name() == "channel_mode":
            self.controller.channel_mode = param.value()
        elif param.name() == "delay":
            self.controller.delay = param.value() * 1e-9
            self.get_actuator_value()
        elif param.name() == "width":
            self.controller.width = param.value() * 1e-9
        elif param.name() == "amplitude_mode":
            self.controller.amplitude_mode = param.value()
        elif param.name() == "amplitude":
            self.controller.amplitude = param.value()
        elif param.name() == "polarity":
            self.controller.polarity = param.value()            
        elif param.name() == "period":
            self.controller.period = param.value()
            self.settings.child('continuous_mode',  'rep_rate').setValue(1 / self.controller.period)
            time.sleep(0.075)
        elif param.name() == "rep_rate":
            self.controller.period = 1 / param.value()
            self.settings.child('continuous_mode',  'period').setValue(self.controller.period)
            time.sleep(0.075)
        elif param.name() == "trig_mode":
            self.controller.trig_mode = param.value()
        elif param.name() == "trig_thresh":
            self.controller.trig_thresh = param.value()
        elif param.name() == "trig_edge":
            self.controller.trig_edge = param.value()
        elif param.name() == "gate_mode":
            self.controller.gate_mode = param.value()
        elif param.name() == "channel_gate_mode":
            self.controller.channel_gate_mode = param.value()
            self.settings.child('gating',  'gate_mode').setValue(self.controller.gate_mode)
            time.sleep(0.075)
        elif param.name() == "gate_thresh":
            self.controller.gate_thresh = param.value()
        elif param.name() == "gate_logic":            
            self.controller.gate_logic = param.value()

    def ini_stage(self, controller=None):
        """Actuator communication initialization

        Parameters
        ----------
        controller: (object)
            custom object of a PyMoDAQ plugin (Slave case). None if only one actuator by controller (Master case)

        Returns
        -------
        info: str
        initialized: bool
            False if initialization failed otherwise True
        """

        self.controller = self.ini_stage_init(old_controller=controller,
                                              new_controller=BNC575("192.168.178.146", 2001))
        
        self.settings.child('connection',  'ip').setValue(self.controller.ip)
        time.sleep(0.05)
        self.settings.child('connection',  'port').setValue(self.controller.port)
        time.sleep(0.05)
        self.controller.restore_state()
        time.sleep(0.05)
        self.get_config()
        

        info = "Whatever info you want to log"
        initialized = True
        return info, initialized


    def move_abs(self, value: DataActuator):
        """ Move the actuator to the absolute target defined by value
        Parameters
        ----------
        value: (float) value of the absolute target positioning
        """
        self.target_value = value
        self.controller.delay = self.target_value * 1e-9
        self.get_actuator_value()

    def move_rel(self, value: DataActuator):
        """ Move the actuator to the relative target actuator value defined by value
        Parameters
        ----------
        value: (float) value of the relative target positioning
        """
        self.target_value = self.current_value + value
        self.controller.delay = self.target_value * 1e-9
        self.get_actuator_value()

    def move_home(self):
        """Call the reference method of the controller"""
        self.controller.delay = 0
        self.get_actuator_value()

    def stop_motion(self):
      """Stop the actuator and emits move_done signal"""
      self.controller.stop()
      self.move_done()
      self.get_actuator_value()


if __name__ == '__main__':
    main(__file__)
