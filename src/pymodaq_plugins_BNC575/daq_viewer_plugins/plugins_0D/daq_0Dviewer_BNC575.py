import numpy as np
import time
from pymodaq_plugins_BNC575.hardware.bnc_commands import BNC575
from pymodaq.utils.daq_utils import ThreadCommand
from pymodaq.utils.data import DataFromPlugins, DataToExport
from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, comon_parameters, main
from pymodaq.utils.parameter import Parameter


class DAQ_0DViewer_BNC575(DAQ_Viewer_base):
    """ Instrument plugin class for a OD viewer.
    
    This object inherits all functionalities to communicate with PyMoDAQ’s DAQ_Viewer module through inheritance via
    DAQ_Viewer_base. It makes a bridge between the DAQ_Viewer module and the Python wrapper of a particular instrument.

    TODO Complete the docstring of your plugin with:
        * This is compatible with the BNC575 Delay/Pulse Generator
        * This was tested with PyMoDAQ version 4.1.0 with Python 3.8.18
        * Installation instructions: what manufacturer’s drivers should be installed to make it run?

    Attributes:
    -----------
    controller: object
        The particular object that allow the communication with the hardware, in general a python wrapper around the
         hardware library.

    """
    params = comon_parameters + [
    {'title': 'Connection', 'name': 'connection', 'type': 'group', 'children': [
        {'title': 'Controller', 'name': 'id', 'type': 'str', 'value': 'BNC,575-4,31309,2.4.1-1.2.2', 'readonly': True},
        {'title': 'IP', 'name': 'ip', 'type': 'str', 'value': '', 'readonly': True},
        {'title': 'Port', 'name': 'port', 'type': 'str', 'value': '', 'readonly': True}
    ]},

    {'title': 'Device Configuration State', 'name': 'config', 'type': 'group', 'children': [
        {'title': 'Configuration Label', 'name': 'label', 'type': 'str', 'value': ""},
        {'title': 'Local Memory Slot', 'name': 'slot', 'type': 'list', 'value': 1, 'limits': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]},
        {'title': 'Save Current Configuration?', 'name': 'save', 'type': 'bool_push', 'label': 'Save', 'value': False},
        {'title': 'Restore Previous Configuration?', 'name': 'restore', 'type': 'bool_push', 'label': 'Restore', 'value': False},
        {'title': 'Reset Device?', 'name': 'reset', 'type': 'bool_push', 'label': 'Reset', 'value': False}
    ]},

    {'title': 'Channel', 'name': 'channel_label', 'type': 'list', 'value': "A", 'limits': ['A', 'B', 'C', 'D']},

    {'title': 'Channel Mode', 'name': 'channel_mode', 'type': 'list', 'value': 'NORM', 'limits': ['NORM', 'SING', 'BURS', 'DCYC']},

    {'title': 'State', 'name': 'state', 'type': 'list', 'value': "OFF", 'limits': ['ON', 'OFF']},

    {'title': 'Width (s)', 'name': 'width', 'type': 'float', 'value': 10e-9, 'default': 10e-9, 'min': 10e-9, 'max': 999.0},
        
    {'title': 'Amplitude (V)', 'name': 'amplitude', 'type': 'float', 'value': 2.0, 'default': 2.0, 'min': 2.0, 'max': 20.0},

    {'title': 'Delay (s)', 'name': 'delay', 'type': 'float', 'value': 0, 'default': 0, 'min': 0, 'max': 999.0},

    {'title': 'Continuous Mode', 'name': 'continuous_mode', 'type': 'group', 'children': [
        {'title': 'Period (s)', 'name': 'period', 'type': 'float', 'value': 1e-3, 'default': 1e-3, 'min': 100e-9, 'max': 5000.0}
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
    
    hardware_averaging = False

    def ini_attributes(self):
        self.controller: BNC575 = None


    def commit_settings(self, param: Parameter):
        """Apply the consequences of a change of value in the detector settings

        Parameters
        ----------
        param: Parameter
            A given parameter (within detector_settings) whose value has been changed by the user
        """
        if param.name() == "label":
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
        elif param.name() == "channel_label":
           self.controller.channel_label = param.value()
           self.grab_data()
        elif param.name() == "state":
            self.controller.state = param.value()
        elif param.name() == "channel_mode":
            self.controller.channel_mode = param.value()
        elif param.name() == "delay":
            self.controller.delay = param.value()
        elif param.name() == "width":
            self.controller.width = param.value()
        elif param.name() == "amplitude":
            self.controller.amplitude = param.value()
        elif param.name() == "period":
            self.controller.period = param.value()
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
        elif param.name() == "gate_thresh":
            self.controller.gate_thresh = param.value()
        elif param.name() == "gate_logic":            
            self.controller.gate_logic = param.value()


    def ini_detector(self, controller=None):
        """Detector communication initialization

        Parameters
        ----------
        controller: (object)
            custom object of a PyMoDAQ plugin (Slave case). None if only one actuator/detector by controller
            (Master case)

        Returns
        -------
        info: str
        initialized: bool
            False if initialization failed otherwise True
        """

        self.ini_detector_init(old_controller=controller,
                               new_controller=BNC575("192.168.178.146", 2001))
        
        self.settings.child('connection',  'ip').setValue(self.controller.ip)
        time.sleep(0.05)
        self.settings.child('connection',  'port').setValue(self.controller.port)
        time.sleep(0.05)
        self.controller.restore_state()
        time.sleep(0.05)
        self.grab_data()

        info = "Whatever info you want to log"
        initialized = True
        return info, initialized

    def close(self):
        """Terminate the communication protocol"""
        self.controller.close()

    def grab_data(self):
        """Start a grab from the detector"""
        
        data_dict = self.controller.output()

        self.settings.child('config',  'label').setValue(data_dict['Configuration Label'])
        time.sleep(0.075)
        self.settings.param('channel_label').setValue(data_dict['Channel'])
        time.sleep(0.075)
        self.settings.param('channel_mode').setValue(data_dict['Channel Mode'])
        time.sleep(0.075)
        self.settings.param('state').setValue(data_dict['State'])
        time.sleep(0.075)
        self.settings.param('width').setValue(data_dict['Width (s)'])
        time.sleep(0.075)
        self.settings.param('amplitude').setValue(data_dict['Amplitude (V)'])
        time.sleep(0.075)
        self.settings.param('delay').setValue(data_dict['Delay (s)'])
        time.sleep(0.075)
        self.settings.child('continuous_mode',  'period').setValue(data_dict['Period (s)'])
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


        # asynchrone version (non-blocking function with callback)
        #raise NotImplemented  # when writing your own plugin remove this line
        #self.controller.your_method_to_start_a_grab_snap(self.callback)  # when writing your own plugin replace this line
        #########################################################


    def callback(self):
        """optional asynchrone method called when the detector has finished its acquisition of data"""
        data_dict = self.controller.your_method_to_get_data_from_buffer()
        self.dte_signal.emit(DataToExport(name='myplugin',
                                          data=[DataFromPlugins(name='Mock1', data=data_dict,
                                                                dim='Data0D', labels=['dat0', 'data1'])]))



if __name__ == '__main__':
    main(__file__)
