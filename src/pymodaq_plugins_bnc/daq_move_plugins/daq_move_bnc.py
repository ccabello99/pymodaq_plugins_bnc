from pymodaq.control_modules.move_utility_classes import DAQ_Move_base, comon_parameters_fun, main, DataActuatorType,\
    DataActuator  # common set of parameters for all actuators
from pymodaq.utils.daq_utils import ThreadCommand # object used to send info back to the main thread
from pymodaq.utils.parameter import Parameter
from pymodaq_plugins_bnc.hardware.bnc_commands import BNC575


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
    is_multiaxes = True
    _axis_names = ['Delay (Channel A)', 'Delay (Channel B)', 'Delay (Channel C)', 'Delay (Channel D)']
    _axis_units = ['ns', 'ns', 'ns', 'ns']
    _epsilon = 0.25
    data_actuator_type = DataActuatorType.DataActuator

    params = comon_parameters_fun(is_multiaxes, axis_names=_axis_names, axis_units=_axis_units, epsilon=_epsilon)

    def ini_attributes(self):
        self.controller: BNC575 = None
        self.attributes = None

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
        self.attributes = self.controller.output()
        


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
            self.controller = self.ini_stage_init(old_controller=None,
                                              new_controller=BNC575(param.value(), port))
        if param.name() == "port":
            ip = self.controller.ip
            self.close()
            self.controller = self.ini_stage_init(old_controller=None,
                                              new_controller=BNC575(ip, param.value()))
        elif param.name() == "label":
            self.controller.label = param.value()
        elif param.name() == "slot":
           self.controller.slot = param.value()
        elif param.name() == "save":
            if param.value:
                self.controller.save_state()
        elif param.name() == "restore":
            if param.value:
                self.controller.restore_state()
                self.get_config()
        elif param.name() == "reset":
            if param.value:
                self.controller.reset()
                self.get_config()
        elif param.name() == "global_state":
            self.controller.global_state = param.value()
        elif param.name() == "global_mode":
            self.controller.global_mode = param.value()
        elif param.name() == "channel_label":
           self.controller.channel_label = param.value()
           self.get_config()
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
        elif param.name() == "rep_rate":
            self.controller.period = 1 / param.value()
            self.settings.child('continuous_mode',  'period').setValue(self.controller.period)
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
        self.settings.child('connection',  'port').setValue(self.controller.port)
        self.controller.restore_state()
        self.attributes = self.controller.output()
        self.settings.addChildren(self.attributes)
        

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

    def update_params_ui(self):

        existing_group_names = {child.name() for child in self.settings.children()}

        for attr in self.attributes:
            attr_name = attr['name']
            if attr.get('type') == 'group':
                if attr_name not in existing_group_names:
                    self.settings.addChild(attr)
                else:
                    group_param = self.settings.child(attr_name)

                    existing_children = {child.name(): child for child in group_param.children()}

                    expected_children = attr.get('children', [])
                    for expected in expected_children:
                        expected_name = expected['name']
                        if expected_name not in existing_children:
                            for old_name, old_child in existing_children.items():
                                if old_child.opts.get('title') == expected.get('title') and old_name != expected_name:
                                    self.settings.child(attr_name, old_name).show(False)
                                    break

                            group_param.addChild(expected)
            else:
                if attr_name not in existing_group_names:
                    self.settings.addChild(attr)


        for param in self.attributes:
            param_type = param['type']
            param_name = param['name']
            
            if param_type == 'group':
                # Recurse over children in groups
                for child in param['children']:
                    child_name = child['name']
                    try:
                        value = child['value']
                    except Exception as e:
                        continue

                    try:
                        # Set the value
                        self.settings.child(param_name, child_name).setValue(value)

                        # Set limits if defined
                        if 'limits' in child and not child.get('readonly', False):
                            try:
                                limits = child['limits']
                                self.settings.child(param_name, child_name).setLimits(limits)
                            except Exception:
                                pass

                    except Exception:
                        pass
            else:
                try:
                    value = param['value']
                except Exception as e:
                    continue

                try:
                    # Set the value
                    self.settings.param(param_name).setValue(value)

                    if 'limits' in param and not param.get('readonly', False):
                        try:
                            limits = param['limits']
                            self.settings.param(param_name).setLimits(limits)
                        except Exception:
                            pass
                except Exception:
                    pass


if __name__ == '__main__':
    main(__file__)
