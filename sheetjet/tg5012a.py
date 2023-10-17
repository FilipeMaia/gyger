"""
Control of the Aim TTi TG5012A function generator.

Based on the manual found at 
https://resources.aimtti.com/manuals/TG5012A_2512A_5011A+2511A_Instructions-Iss8.pdf
"""

import socket
import serial
import logging

class TG5012A:
    def __init__(self, serial_port = None, address='t539639.local', port=9221, auto_local=True):
        self.terminator = b'\n'
        self.ser = None
        self.sock = None
        if serial_port is not None:
            # Prefer serial over LAN communication        
            ser = serial.Serial(port = serial_port)
            ser.open()
            if(ser.is_open != True):
                raise ConnectionError("Serial port failed to open")
            self.ser = ser
            logging.info("Successfully connected to %s" % (serial_port))            
        else:
            # Open LAN connection
            self.sock = socket.socket()
            self.sock.connect((address, port))
            self.auto_local = auto_local
            logging.info("Successfully connected to %s:%d" % (address, port))
        print(self.id())

        

    
    # Convenience functions
    def pulse(self, freq=1, width=0.1, rise = 0.001, fall = 0.001, high=1, low=0, delay = 0, phase=0, output = "ON"):
        """Sets the output to a pulse with the given parameters"""
        self.wave("PULSE")
        self.frequency(freq)
        self.pulse_width(width)
        self.pulse_rise(rise)
        self.pulse_fall(fall)
        self.pulse_delay(delay)
        self.high(high)
        self.low(low)
        self.phase(phase)
        self.output(output)

    
    # Channel Selection
    def channel(self, set = None):
        """Queries or sets the active channel"""
        if(set is None):
            return self.query("CHN?")        
        return self.set("CHN", str(set))

    # Continuous Carrier Wave Commands
    def wave(self, set = "PULSE"):
        """Sets the output waveform"""
        return self.set("WAVE", str(set))
    
    def frequency(self, set = 1):
        """Sets the output frequency"""
        return self.set("FREQ", str(set))
    
    def amplitude(self, set = 1):
        """Sets the output amplitude"""
        return self.set("AMPL", str(set))
        
    def high(self, set = 1):
        """Sets the amplitude high level"""
        return self.set("HILVL", str(set))
    
    def low(self, set = 0):
        """Sets the amplitude low level"""
        return self.set("LOLVL", str(set))
    
    def output(self, set = "ON"):
        """Sets the output on, off, normal or invert"""
        return self.set("OUTPUT", set)
    
    def output_load(self, set = 50):
        """Sets the output load, in Ohms"""
        return self.set("ZLOAD", str(set))

    def phase(self, set = 0):
        """Sets the output phase, in degrees"""
        return self.set("PHASE", str(set))
    
    def align(self):
        """Sends signal to align zero phase reference of both channels"""
        return self.set("ALIGN")
    
    # Pulse Generator Commands

    def pulse_frequency(self, set = 1):
        """Sets the pulse frequency in Hz"""
        return self.set("PULSFREQ", str(set))
    
    def pulse_width(self, set = 1):
        """Sets the pulse width in seconds"""
        return self.set("PULSWID", str(set))

    def pulse_rise(self, set = 0.001):
        """Sets the pulse rise time in seconds"""
        return self.set("PULSRISE", str(set))
    
    def pulse_fall(self, set = 0.001):
        """Sets the pulse fall time in seconds"""
        return self.set("PULSFALL", str(set))
    
    def pulse_delay(self, set = 0):
        """Sets the pulse delay in seconds"""
        return self.set("PULSDLY", str(set))

    # System and Status Commands
    def query_error(self):
        """Query and clear Query Error Register"""
        return self.query("QER?")
    
    def execution_error(self):
        """Query and clear Execution Error Register"""
        return self.query("EER?")
    
    def clear_status(self):
        """Clears the status registers"""
        return self.set("*CLS")

    def reset(self):
        """Resets the instrument"""
        return self.set("*RST")
    
    def save(self, addr = 1):
        """Saves the current settings to a non-volatile memory location."""
        return self.set("*SAV", str(addr))
    
    def recall(self, addr = 1):
        """Recalls settings from a non-volatile memory location."""
        return self.set("*RCL", str(addr))
    
    def id(self):
        """Returns the ID string of the instrument"""
        return self.query("*IDN?")
    
    def wait_for_completion(self):
        """Waits for the instrument to complete its tasks"""
        return self.query("*OPC?")
    
    def local(self):
        """Sets the instrument to local mode"""
        return self.set("LOCAL")    

    def query(self, cmd):
        self.write(cmd)
        ret = self.read()
        if(self.auto_local and cmd != "LOCAL"):
            self.local()
        return ret
    
    def set(self, cmd, value=None):
        if(value is None):
            ret = self.write(cmd)
        else:
            ret = self.write(cmd + ' ' + str(value))
        if(self.auto_local and cmd != "LOCAL"):
            self.local()        
        return ret
    
    def write(self, str):
        """Write str to the instrument encoded as ascii as terminated"""
        bytes = str.encode('ascii') + self.terminator
        if self.sock:
            return self.sock.send(bytes)
        elif self.ser:
            return self.ser.write(bytes)
        else:
            raise ConnectionError("No connection to instrument")
        
    def read(self):
        """Read line from the instrument"""
        if self.sock:
            recv = self.sock.recv(1024)
            return recv.decode('ascii').strip()
        elif self.ser:
            return self.ser.readline().decode('ascii').strip()
        else:
            raise ConnectionError("No connection to instrument")        