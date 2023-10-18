import serial
from dataclasses import dataclass
from typing import Tuple

class VCMini:
    def __init__(self, serial_port = 'COM6', baudrate=38400, timeout_s=1):
        """
        Open communication with valve controller VC-Mini

        Also sets the module address to 0, active parameter set to 0 and 
        reads the current parameters loaded.
        """
        ser = serial.Serial()
        ser.baudrate = baudrate
        ser.port = serial_port
        ser.parity = serial.PARITY_NONE
        ser.bytesize = serial.EIGHTBITS
        ser.stopbits = serial.STOPBITS_ONE
        ser.timeout = timeout_s # seconds
        ser.open()
        if(ser.is_open != True):
            raise ConnectionError("Serial port failed to open")
        self.ser = ser
        # Set an initial address        
        self.address(0)
        # Set an initial parameter set
        self.load_parameters(0)

        self.eeprom = EEPROM()
        print(self.eeprom.addr[0].params[7])
        self.eeprom.addr[0].params[7].cycle_time = 1000
        print(self.eeprom.addr[0].params[7])
        self.init_ram()


    def init_ram(self):
        """Initialize RAM with default parameters."""
        self.ram = ValveParameters()
        self.ram.peak_time = self.peak_time()
        self.ram.open_time = self.open_time()
        self.ram.cycle_time = self.cycle_time()
        self.ram.peak_current = self.peak_current()
        self.ram.num_shots = self.num_shots()


    def peak_time(self, set = None, override_limits = False):
        """Query or set peak current time to initiate valve opening, in us."""
        if(set is None):
            return self.query(b'a')
        else:
            if(set < 100 or set  > 500) and not override_limits:
                raise ValueError("Peak time must be between 100 and 500 us")
            return self.set_parameter(b'A', set)

    def open_time(self, set = None, override_limits = False):
        """Query or set valve open time in us."""
        if(set is None):
            return self.query(b'b')
        else:
            if (set < 400 or set > 9999999) and not override_limits:
                raise ValueError("Open time must be between 400 and 9999999 us")
            self.set_parameter(b'B', set)

    def cycle_time(self, set = None):
        """Query or set firing frequency in us."""
        if(set is None):
            return self.query(b'c')
        else:
            if set < 10 or set > 9999999:
                raise ValueError("Cycle time must be between 10 and 9999999 us")
            return self.set_parameter(b'C', set)
    
    def peak_current(self, set = None):
        """
        Query or set peak current parameter D. 
        The actual peak current I_p is given by I_p = 450mA + (D * 50mA) us. 
        Should be kept at 1 A (meaning value 11).
        """
        if(set is None):
            return self.query(b'd')
        else:
            if set < 0 or set > 15:
                raise ValueError("Peak current must be between 0 and 15")
            return self.set_parameter(b'D', set)
        
    def num_shots(self, set = None):
        """Query or set number of shots to fire before stopping. 0 means infinite."""
        if(set is None):
            return self.query(b'g')
        else:
            if set < 0 or set > 65535:
                raise ValueError("Number of shots must be between 0 and 65535")
            return self.set_parameter(b'G', set)

    def valve_status(self):
        """Returns the active status for each of the two valves as a tuple."""
        v = self.query(b'q')
        return (v & 0x10, v & 0x01)
    
    def shot_counter(self, valve):
        """Returns the shot counter for the specified valve.
        
        The shot counter is volatile, at power-on it is set to 0.
        """
        if valve == 0:
            return self.query(b'y')
        elif valve == 1:
            return self.query(b'z')
        else:
            raise Exception("Invalid valve number")
        
    def zero_shot_counter(self, valve):
        """Zero the shot counter for the specified valve."""
        if valve == 0:
            return self.execute(b'I')
        elif valve == 1:
            return self.execute(b'J')
        else:
            raise ValueError("Invalid valve number")

    def total_shot_counter(self, valve):
        """Returns the total shot counter for the specified valve."""
        if valve == 0:
            high = self.query(b'u')
            low = self.query(b'v')
            return (high<<24) | low
        elif valve == 1:
            high = self.query(b'w')
            low = self.query(b'x')
            return (high<<24) | low
        else:
            raise ValueError("Invalid valve number")

    def address(self, set = None):
        """
        Query or set the current module address of the valve controller.
        Returns the module address and module type as a tuple.
        """
        if(set is not None):
            return self.set_parameter(b'*', set)
        else:
            value = self.query(b'=')
            addr = value[0]
            module_type = value[1:]
            return addr, module_type

    def load_parameters(self, position = None):
        """
        Loads the a parameter set from the given EEPROM position.
        If position is `None` return the current parameters position.
        """
        if(position is None):
            return self.query(b'p')
        else:
            if position < 0 or position > 7:
                raise ValueError("Parameter position must be between 0 and 7")
            return self.query(b'n', position)

    def save_parameters(self, position = None):
        """
        Saves the active set of parameters to the given EEPROM position.
        If position is `None` return the current parameters position.
        """
        if(position is None):
            return self.query(b'p')
        else:
            if position < 0 or position > 7:
                raise ValueError("Parameter position must be between 0 and 7")
            return self.set_parameter(b'N', position)
            
    SINGLE = b'X'
    PULSE = b'T'
    SERIES = b'P'
    PULSE_SERIES = b'L'
    NONE = b'S'
    def trigger_mode(self, trigger=None):
        """
        Set the trigger mode.

        While a trigger mode is active, no further entries are possible on the corresponding module.
        Only the command ``trigger_mode(VCMini.NONE)`` (stop of a external trigger mode) can be performed.

        Parameters
        ----------
        trigger: {VCMini.SINGLE, VCMini.PULSE, VCMini.SERIES, VCMini.PULSE_SERIES, VCMini.NONE}
        * VCMini.SINGLE : Arm single shot on valves V1 and V2 triggered via external hardware trigger
        * VCMini.PULSE : Arm single shot on valves V1 and V2 with the opening time controlled by the length of the external hardware trigger
        * VCMini.SERIES : Arm shot series on valves V1 and V2 triggered via external hardware trigger
        * VCMini.PULSE_SERIES : Arm shot series on valves V1 and V2 which continues for as long as the external hardware trigger stays high
        * VCMini.NONE : Exit external trigger mode and disarm all triggers
        """
        if trigger is None:
            trigger = VCMini.NONE
        if trigger not in [VCMini.SINGLE, VCMini.PULSE, VCMini.SERIES, VCMini.PULSE_SERIES, VCMini.NONE]:
            raise ValueError("Invalid trigger mode")
        return self.execute(trigger)
    
    V1 = b'Y'
    V2 = b'Z'
    V1V2 = b'V'
    SERIES_V1 = b'Q'
    SERIES_V2 = b'R'
    FOREVER_V1V2 = b'U'
    STOP = b'S'
    def fire(self, mode=None):
        """
        Open the valves according to the specified mode using a software trigger.

        The command delay after receiving the command character until the first shot is fired is approximately
        2ms. For time-critical applications you should use the capabilities of shot with hardware trigger.

        Parameters
        ----------
        mode: {VCMini.V1, VCMini.V2, VCMini.V1V2, 
        VCMini.SERIES_V1, VCMini.SERIES_V2,
        VCMini.FOREVER_V1V2, VCMini.STOP}
        * VCMini.V1 : Single shot of the V1 valve
        * VCMini.V2 : Single shot of the V2 valve
        * VCMini.V1V2 : Single shot of both valves simultaneously
        * VCMini.SERIES_V1 : Series of shots of the V1 valve until num_shots() is reached
        * VCMini.SERIES_V2 : Series of shots of the V2 valve until num_shots() is reached
        * VCMini.FOREVER_V1V2 : Series of shots of both valves until until VCMini.STOP is issued
        * VCMini.STOP : Stop any series of shots
        """
        if mode is None:
            mode = VCMini.STOP
        if mode not in [VCMini.V1, VCMini.V2, VCMini.V1V2, VCMini.SERIES_V1, VCMini.SERIES_V2, VCMini.FOREVER_V1V2, VCMini.STOP]:
            raise ValueError("Invalid trigger mode")
        return self.execute(mode)


    

    def execute(self, param):
        """
        Send an execution command to the controller.
        Execution commands are defined in the Gyger VC Mini manual.
        """
        if len(param) != 1:
            raise ValueError("Invalid parameter")
        self.ser.write(b'%c' % param)
        line = self.ser.readline()
        if(line[:2] != b'%c' % param):
            raise Exception("Error reading %s. Got %s" % (param, line))
        prompt = self.ser.read(2)
        if(prompt != b'\r>'):
            raise Exception("Error reading %s" % (param))

    def set_parameter(self, param, value):
        """
        Send a parametrization command to the controller.
        Parametrization commands are defined in the Gyger VC Mini manual.
        """
        if len(param) != 1:
            raise ValueError("Invalid parameter")
        if(not isinstance(value, int)):
            raise ValueError("Value must be an integer")
        
        self.ser.write(b'%d%c' % (value,param))
        line = self.ser.readline()

        if(line[:-1] != b'%d%c' % (value,param)):
                raise Exception("Error reading %s. Got %s" % (param, line))
        prompt = self.ser.read(2)
        if(prompt != b'\r>'):
            raise Exception("Error reading %s" % (param))
        value = int(line[-2])
        return value
                    
    def query(self, param, value=None):
        """
        Send a query command parameters to the controller.
        Query command parameters are defined in the Gyger VC Mini manual.
        """
        if len(param) != 1:
            raise ValueError("Invalid parameter")
        if(value is None):
            self.ser.write(b'%c' % param)
            output = b'.%c' % (param)
        else:
            if(not isinstance(value, int)):
                raise ValueError("Value must be an integer")
            if(param != b'n'):
                raise ValueError("Value can only be set when param=b'n'")
            self.ser.write(b'%d%c' % (value,param))
            output = b'%d.%c' % (value, param)
        line = self.ser.readline()

        if(line[:len(output)] != output):
            raise Exception("Error reading %c. Got %s" % (param,line))
        prompt = self.ser.read(2)
        if(prompt != b'\r>'):
            raise Exception("Error reading %c" % (param))
        
        if(value is None):
            value = line[len(output):-1]
            try:
                # Some return values are not integers
                value = int(value)
            except ValueError:
                pass

        return value

@dataclass
class ValveParameters:
    """Set of valve control parameters."""
    peak_time: int = 150 # in us. Peak current time to initiate valve opening, also known as A in the manual
    open_time: int = 100000 # in us. Valve open time, also known as B in the manual
    cycle_time: int = 1000000 # in us. Firing frequency, also known as C in the manual
    peak_current: int = 11 # Also known as D in the manual. The actual peak current
                      #I_p is given by I_p = 450mA + (D * 50mA) us. Should be kept at 1 A (meaning value 11)
    num_shots: int = 1 # Number of shots to fire before stopping. 0 means infinite. Also known as G in the manual

@dataclass
class ParameterSet:
    """Set of 8 valve control parameters. The EEPROM can store 9 sets of parameters."""
    params: Tuple[ValveParameters] = tuple(ValveParameters() for i in range(8))

@dataclass
class EEPROM:
    """Set of 9 parameter sets."""
    addr: Tuple[ParameterSet] = tuple(ParameterSet() for i in range(9))


