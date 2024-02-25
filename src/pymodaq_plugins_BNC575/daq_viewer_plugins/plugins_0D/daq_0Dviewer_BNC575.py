import numpy as np
from pymodaq_plugins_BNC575.hardware.bnc_commands import BNC575
from pymodaq.utils.daq_utils import ThreadCommand
from pymodaq.utils.data import DataFromPlugins, DataToExport
from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, comon_parameters, main
from pymodaq.utils.parameter import Parameter


# TODO:
# (3) this file should then be put into the right folder, namely IN THE FOLDER OF THE PLUGIN YOU ARE DEVELOPING:
#     pymodaq_plugins_my_plugin/daq_viewer_plugins/plugins_0D
class DAQ_0DViewer_BNC575(DAQ_Viewer_base):
    """ Instrument plugin class for a OD viewer.
    
    This object inherits all functionalities to communicate with PyMoDAQ’s DAQ_Viewer module through inheritance via
    DAQ_Viewer_base. It makes a bridge between the DAQ_Viewer module and the Python wrapper of a particular instrument.

    TODO Complete the docstring of your plugin with:
        * The set of instruments that should be compatible with this instrument plugin.
        * With which instrument it has actually been tested.
        * The version of PyMoDAQ during the test.
        * The version of the operating system.
        * Installation instructions: what manufacturer’s drivers should be installed to make it run?

    Attributes:
    -----------
    controller: object
        The particular object that allow the communication with the hardware, in general a python wrapper around the
         hardware library.

    """
    params = comon_parameters + [
    {'title': 'Connection', 'name': 'connection', 'type': 'group', 'children': [
        {'title': 'Controller', 'name': 'controllerid', 'type': 'str', 'value': '', 'readonly': True},
        {'title': 'IP', 'name': 'ip', 'type': 'str', 'value': "192.168.178.146"},
        {'title': 'Port', 'name': 'port', 'type': 'int', 'value': 2001}
    ]},

    {'title': 'Configuration Label', 'name': 'config', 'type': 'group', 'children': [
        {'title': 'Set New Label?', 'name': 'command', 'type': 'bool', 'value': False},
        {'title': 'Label', 'name': 'label', 'type': 'str', 'value': ""}
    ]},

    {'title': 'Channel Label', 'name': 'channel_label', 'type': 'str', 'value': "A", 'default': "A"},

    {'title': 'Channel State', 'name': 'state', 'type': 'str', 'value': "OFF"},

    {'title': 'Continuous Mode', 'name': 'continuous_mode', 'type': 'group', 'children': [
        {'title': 'Channel Mode', 'name': 'channel_mode', 'type': 'str', 'value': 'NORM'},
        {'title': 'Pulse Period (s)', 'name': 'period', 'type': 'float', 'value': 1e-3, 'default': 1e-3, 'min': 100e-9, 'max': 5000.0},
        {'title': 'Pulse Delay (s)', 'name': 'delay', 'type': 'float', 'value': 0, 'default': 0, 'min': 0, 'max': 999.0},
        {'title': 'Pulse Width (s)', 'name': 'width', 'type': 'float', 'value': 10e-9, 'default': 10e-9, 'min': 10e-9, 'max': 999.0},
        {'title': 'Pulse Amplitude (V)', 'name': 'amplitude', 'type': 'float', 'value': 2.0, 'default': 2.0, 'min': 2.0, 'max': 20.0}
    ]},

    {'title': 'Trigger Mode', 'name': 'trigger_mode', 'type': 'group', 'children': [
        {'title': 'Channel Mode', 'name': 'channel_mode', 'type': 'str', 'value': 'SING'},
        {'title': 'Trigger Mode', 'name': 'trig_mode', 'type': 'str', 'value': 'DIS'},
        {'title': 'Pulse Delay (s)', 'name': 'delay', 'type': 'float', 'value': 0, 'default': 0, 'min': 0, 'max': 999.0},
        {'title': 'Pulse Width (s)', 'name': 'width', 'type': 'float', 'value': 10e-9, 'default': 10e-9, 'min': 10e-9, 'max': 999.0},
        {'title': 'Pulse Amplitude (V)', 'name': 'amplitude', 'type': 'float', 'value': 2.0, 'default': 2.0, 'min': 2.0, 'max': 20.0},
        {'title': 'Trigger Threshold (V)', 'name': 'trigger_threshold', 'type': 'float', 'value': 2.5, 'default': 2.5, 'min': 0.2, 'max': 15.0},
        {'title': 'Trigger on Rising Edge', 'name': 'rising', 'type': 'bool', 'value': True}
    ]},

    {'title': 'Gate Function', 'name': 'gating', 'type': 'group', 'children': [
        {'title': 'Channel Mode', 'name': 'channel_mode', 'type': 'str', 'value': 'SING'},
        {'title': 'Channel Gate Mode', 'name': 'channel_gate_mode', 'type': 'str', 'value': "DIS"},
        {'title': 'Gate Threshold (V)', 'name': 'gate_threshold', 'type': 'float', 'value': 2.5, 'default': 2}
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
        if param.name() == "channel_label":
           self.controller.set_channel = param.value()
        elif param.name() == "label":
            self.controller.label = param.value()
        elif param.name() == "state":
            self.controller.state = param.value()
        elif param.name() == "channel_mode":
            self.controller.channel_mode = param.value()
        elif param.name() == "period":
            self.controller.period = param.value()
        elif param.name() == "delay":
            self.controller.delay = param.value()
        elif param.name() == "width":
            self.controller.width = param.value()
        elif param.name() == "amplitude":
            self.controller.amplitude = param.value()
        elif param.name() == "trigger_mode":
            self.controller.trig_mode = param.value()
        elif param.name() == "trigger_threshold":
            self.controller.trig_thresh = param.value()
        elif param.name() == "rising":
            self.controller.trig_edge = param.value()
        elif param.name() == "channel_gate_mode":
            self.controller.channel_gate_mode = param.value()
        elif param.name() == "gate_threshold":
            self.controller.gate_thresh = param.value()
        elif param.name() == "high":            
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

        # TODO for your custom plugin (optional) initialize viewers panel with the future type of data
        self.dte_signal_temp.emit(DataToExport(name='BNC575',
                                               data=[DataFromPlugins(name='Mock1',
                                                                    data=[np.array([0]), np.array([0])],
                                                                    dim='Data0D',
                                                                    labels=['Mock1', 'label2'])]))

        info = "Whatever info you want to log"
        initialized = True
        return info, initialized

    def close(self):
        """Terminate the communication protocol"""
        self.controller.close()

    def grab_data(self, Naverage=1, **kwargs):
        """Start a grab from the detector

        Parameters
        ----------
        Naverage: int
            Number of hardware averaging (if hardware averaging is possible, self.hardware_averaging should be set to
            True in class preamble and you should code this implementation)
        kwargs: dict
            others optionals arguments
        """
        ## TODO for your custom plugin: you should choose EITHER the synchrone or the asynchrone version following

        # synchrone version (blocking function)
        data_dict = self.controller.output()
        data_tot = np.array(list(data_dict.values()))
        data_labels = list(data_dict.keys())
        self.dte_signal.emit(DataToExport(name='myplugin',
                                          data=[DataFromPlugins(name='Mock1', data=data_tot,
                                                                dim='Data0D', labels=data_labels)]))
        #########################################################

        # asynchrone version (non-blocking function with callback)
        #raise NotImplemented  # when writing your own plugin remove this line
        #self.controller.your_method_to_start_a_grab_snap(self.callback)  # when writing your own plugin replace this line
        #########################################################


    def callback(self):
        """optional asynchrone method called when the detector has finished its acquisition of data"""
        data_tot = self.controller.your_method_to_get_data_from_buffer()
        self.dte_signal.emit(DataToExport(name='myplugin',
                                          data=[DataFromPlugins(name='Mock1', data=data_tot,
                                                                dim='Data0D', labels=['dat0', 'data1'])]))



if __name__ == '__main__':
    main(__file__)
