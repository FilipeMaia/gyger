import serial
from dataclasses import dataclass
from typing import Tuple

class VCMini:
    def __init__(self, port = 'COM1', baudrate=38400, timeout_s=1):
        # Open communication with valve controller VC-Mini
        ser = serial.Serial()
        ser.baudrate = baudrate
        ser.port = port
        ser.parity = serial.PARITY_NONE
        ser.bytesize = serial.EIGHTBITS
        ser.stopbits = serial.STOPBITS_ONE
        ser.timeout = timeout_s # seconds
        if(0):
            ser.open()
            assert ser.is_open == True, "Serial port failed to open"
        self.ser = ser
                
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


    def peak_time(self, set = None):
        if(set is None):
            return self.read_value(b'a')
        else:
            return self.write_value(b'a', set)

    def open_time(self):
        return self.read_value(b'b')
    
    def cycle_time(self):
        return self.read_value(b'c')
    
    def peak_current(self):
        return self.read_value(b'd')

    def num_shots(self):
        return self.read_value(b'g')

    def active_parameter_set(self):
        return self.read_value(b'p')

    def valve_status(self):
        """Returns the active status for each of the two valves as a tuple"""
        v = self.read_value(b'q')
        return (v & 0x10, v & 0x01)
    
    def shot_counter(self, valve):
        """Returns the shot counter for the specified valve"""
        if valve == 0:
            return self.read_value(b'y')
        elif valve == 1:
            return self.read_value(b'z')
        else:
            raise Exception("Invalid valve number")

    def total_shot_counter(self, valve):
        """Returns the total shot counter for the specified valve"""
        if valve == 0:
            high = self.read_value(b'u')
            low = self.read_value(b'v')
            return (high<<24) | low
        elif valve == 1:
            high = self.read_value(b'w')
            low = self.read_value(b'x')
            return (high<<24) | low
        else:
            raise Exception("Invalid valve number")

    def read_value(self, param):
        if len(param) != 1:
            raise Exception("Invalid parameter")
        self.ser.write(b'%c' % param)
        line = self.ser.readline()
        if(line[:2] != b'.%c' % param):
            raise Exception("Error reading %c" % (param))
        prompt = self.ser.read(2)
        if(prompt != b'\r>'):
            raise Exception("Error reading %c" % (param))
        value = int(line[2:])
        return value
    
    def set_value(self, param, value):
        if len(param) != 1:
            raise Exception("Invalid parameter")
        self.ser.write(b'%d%c' % (value,param))
        line = self.ser.readline()
        if(line[:2] != b'.%d%c' % (value,param)):
            raise Exception("Error reading %c" % (param))
        prompt = self.ser.read(2)
        if(prompt != b'\r>'):
            raise Exception("Error reading %c" % (param))
        value = int(line[2:])
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

test = VCMini()


