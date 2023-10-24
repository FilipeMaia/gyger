import serial
from dataclasses import dataclass
from typing import Tuple
import logging

class VCMini:
    """
    Control a Gyger VC Mini valve controller.

    Based on the "Manual serial interface VC Mini rev 2.00 en" found at https://www.fgyger.ch/downloads/?lang=en   
    """
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
        logging.info("Successfully connected to VCMIni on %s" % (serial_port))

    def close(self):
        """
        Close the serial connection.
        """
        self.ser.close()

    def reopen(self):
        """Reopen the serial connection."""
        self.ser.open()
        if(self.ser.is_open != True):
            raise ConnectionError("Serial port failed to open")
        self.init_ram()
        logging.info("Successfully connected to VCMIni on %s" % (self.ser.port))

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
            return self.query('a')
        else:
            if(set < 100 or set  > 500) and not override_limits:
                raise ValueError("Peak time must be between 100 and 500 us")
            return self.set_parameter('A', set)

    def open_time(self, set = None, override_limits = False):
        """Query or set valve open time in us."""
        if(set is None):
            return self.query('b')
        else:
            if (set < 400 or set > 9999999) and not override_limits:
                raise ValueError("Open time must be between 400 and 9999999 us")
            self.set_parameter('B', set)

    def cycle_time(self, set = None):
        """Query or set firing frequency in us."""
        if(set is None):
            return self.query('c')
        else:
            if set < 10 or set > 9999999:
                raise ValueError("Cycle time must be between 10 and 9999999 us")
            return self.set_parameter('C', set)
    
    def peak_current(self, set = None):
        """
        Query or set peak current parameter D. 
        The actual peak current I_p is given by I_p = 450mA + (D * 50mA) us. 
        Should be kept at 1 A (meaning value 11).
        """
        if(set is None):
            return self.query('d')
        else:
            if set < 0 or set > 15:
                raise ValueError("Peak current must be between 0 and 15")
            return self.set_parameter('D', set)
        
    def num_shots(self, set = None):
        """Query or set number of shots to fire before stopping. 0 means infinite."""
        if(set is None):
            return self.query('g')
        else:
            if set < 0 or set > 65535:
                raise ValueError("Number of shots must be between 0 and 65535")
            return self.set_parameter('G', set)

    def valve_status(self):
        """Returns the active status for each of the two valves as a tuple."""
        v = self.query('q')
        return (v & 0x10, v & 0x01)
    
    def shot_counter(self, valve):
        """Returns the shot counter for the specified valve.
        
        The shot counter is volatile, at power-on it is set to 0.
        """
        if valve == 0:
            return self.query('y')
        elif valve == 1:
            return self.query('z')
        else:
            raise Exception("Invalid valve number")
        
    def zero_shot_counter(self, valve):
        """Zero the shot counter for the specified valve."""
        if valve == 0:
            return self.execute('I')
        elif valve == 1:
            return self.execute('J')
        else:
            raise ValueError("Invalid valve number")

    def total_shot_counter(self, valve):
        """Returns the total shot counter for the specified valve."""
        if valve == 0:
            high = self.query('u')
            low = self.query('v')
            return (high<<24) | low
        elif valve == 1:
            high = self.query('w')
            low = self.query('x')
            return (high<<24) | low
        else:
            raise ValueError("Invalid valve number")

    def address(self, set = None):
        """
        Query or set the current module address of the valve controller.
        Returns the module address and module type as a tuple.
        """
        if(set is not None):
            return self.set_parameter('*', set)
        else:
            value = self.query('=')
            if(len(value) != 2):
                return value
            addr = value[0]
            module_type = value[1:]
            return addr, module_type
            

    def load_parameters(self, position = None):
        """
        Loads the a parameter set from the given EEPROM position.
        If position is `None` return the current parameters position.
        """
        if(position is None):
            return self.query('p')
        else:
            if position < 0 or position > 7:
                raise ValueError("Parameter position must be between 0 and 7")
            return self.query('n', position)

    def save_parameters(self, position = None):
        """
        Saves the active set of parameters to the given EEPROM position.
        If position is `None` return the current parameters position.
        """
        if(position is None):
            return self.query('p')
        else:
            if position < 0 or position > 7:
                raise ValueError("Parameter position must be between 0 and 7")
            return self.set_parameter('N', position)
            
    def trigger_mode(self, mode='stop'):
        """
        Set the trigger mode.

        While a trigger mode is active, no further entries are possible on the corresponding module.
        Only the command ``trigger_mode('stop')`` (exit external trigger mode) can be performed.

        Parameters
        ----------
        mode: {'single', 'pulse', 'series', 'pulse series', 'stop'}
            * 'single' : Arm single shot on valves V1 and V2 triggered via external hardware trigger
            * 'pulse' : Arm single shot on valves V1 and V2 with the opening time controlled by the length of the external hardware trigger
            * 'series' : Arm shot series on valves V1 and V2 triggered via external hardware trigger
            * 'pulse series' : Arm shot series on valves V1 and V2 which continues for as long as the external hardware trigger stays high
            * 'stop' : Exit external trigger mode and disarm all triggers
        """
        cmd_dict = {'single': 'X', 'pulse': 'T', 'series': 'P', 'pulse series': 'L', 'stop': 'S'}
        if mode not in cmd_dict:
            raise ValueError("Invalid trigger mode")
        return self.execute(cmd_dict[mode])
    
    def fire(self, shot='stop'):
        """
        Open the valves according to the specified mode using a software trigger.

        The command delay after receiving the command character until the first shot is fired is approximately
        2ms. For time-critical applications you should use the capabilities of shot with hardware trigger.

        Parameters
        ----------
        shot: {'v1', 'v2', 'both', 'series v1', 'series v2', 'series both', 'stop'} 
            * 'v1' : Single shot of the v1 valve
            * 'v2' : Single shot of the v2 valve
            * 'both' : Single shot of both valves simultaneously
            * 'series v1' : Series of shots of the v1 valve until num_shots() is reached
            * 'series v2' : Series of shots of the v2 valve until num_shots() is reached
            * 'series both' : Series of shots of both valves until until 'stop' is issued
            * 'stop' : Stop any series of shots
        """
        cmd_dict = {'v1': 'Y', 'v2': 'Z', 'both': 'V', 'series v1': 'Q', 'series v2': 'R', 'series both': 'U', 'stop': 'S'}
        if shot not in cmd_dict:
            raise ValueError("Invalid shot")
        return self.execute(cmd_dict[shot])


    

    def execute(self, param):
        """
        Send an execution command to the controller.
        Execution commands are defined in the Gyger VC Mini manual.
        """
        if len(param) != 1:
            raise ValueError("Invalid parameter")
        self.ser.write(param.encode('ascii'))
        ret = self.ser.read_until('>').decode('ascii')
        line = ret.split('\n')[0]
        if(line != param):
            if line == '?':
                logging.warning('Valve is busy!')
            else:            
                raise Exception("Error reading %s. Got %s" % (param, ret))
        prompt = ret.split('\n')[1]
        if(prompt != '\r>'):
            raise Exception("Error reading %s. Got %s" % (param, ret))

    def set_parameter(self, param, value):
        """
        Send a parametrization command to the controller.
        Parametrization commands are defined in the Gyger VC Mini manual.
        """
        if len(param) != 1:
            raise ValueError("Invalid parameter")
        if(not isinstance(value, int)):
            raise ValueError("Value must be an integer")
        
        self.ser.write(('%d%s' % (value,param)).encode('ascii'))
        ret = self.ser.read_until('>').decode('ascii')
        line = ret.split('\n')[0]

        if(line != '%d%s' % (value,param)):
            if line == '?':
                logging.warning('Valve is busy!')
            else:                
                raise Exception("Error reading %s. Got %s" % (param, ret))
        prompt = ret.split('\n')[1]
        if(prompt != '\r>'):
            raise Exception("Error reading %s. Got %s" % (param, ret))
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
            self.ser.write(param.encode('ascii'))
            output = '.%s' % (param)
        else:
            if(not isinstance(value, int)):
                raise ValueError("Value must be an integer")
            if(param != 'n'):
                raise ValueError("Value can only be set when param='n'")
            self.ser.write(('%d%s' % (value,param)).encode('ascii'))
            output = '%d.%s' % (value, param)
        ret = self.ser.read_until('>').decode('ascii')
        line = ret.split('\n')[0]

        if(line[:len(output)] != output):
            if line == '?':
                logging.warning('Valve is busy!')
            else:
                raise Exception("Error reading %s. Got %s" % (param, ret))
        prompt = ret.split('\n')[1]
        if(prompt != '\r>'):
            raise Exception("Error reading %s. Got %s" % (param, ret))
        
        if(value is None):
            value = line[len(output):]
            try:
                # Some return values are not integers
                value = int(value)
            except ValueError:
                pass

        return value

@dataclass
class ValveParameters:
    """
    Set of valve control parameters.
    
    Args:
        peak_time: Peak current time to initiate valve opening, also known as A in the manual. Given in us.
        open_time: Valve open time, also known as B in the manual. Given in us.
        cycle_time: Firing frequency, also known as C in the manual. Given in us.
        peak_current: The actual peak current I_p is given by I_p = 450mA + (D * 50mA) us. Should be kept at 1 A (meaning value 11)
        num_shots: Number of shots to fire before stopping. 0 means infinite. Also known as G in the manual    
    """
    peak_time: int = 150
    open_time: int = 100000
    cycle_time: int = 1000000
    peak_current: int = 11
    num_shots: int = 1

@dataclass
class ParameterSet:
    """Set of 8 valve control parameters. The EEPROM can store 9 sets of parameters.
    
    Args:
        params: Tuple of 8 ValveParameters objects.

    :meta private:
    """
    params: Tuple[ValveParameters] = tuple(ValveParameters() for i in range(8))

@dataclass
class EEPROM:
    """Set of 9 parameter sets.
    
    :meta private:
    """
    addr: Tuple[ParameterSet] = tuple(ParameterSet() for i in range(9))


