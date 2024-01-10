

import socket
import serial
import logging

class TG5012A:
    """
    Control of the Aim TTi TG5012A function generator.

    Based on the manual found at 
    https://resources.aimtti.com/manuals/TG5012A_2512A_5011A+2511A_Instructions-Iss8.pdf
    """
    def __init__(self, serial_port = None, address='t539639.local', port=9221, auto_local=True, error_check=True):
        """Connects to a TF5012A function generator using the given serial_port or LAN address and port
        
        If auto_local is true (default), the instrument will be set to local mode after each command.
        if error_check is true (default), the instrument will check for errors after each command.
        """
        self.terminator = b'\n'
        self.ser = None
        self.sock = None
        self.auto_local = auto_local
        self.error_check = error_check
        if serial_port is not None:
            # Prefer serial over LAN communication        
            ser = serial.Serial(port = serial_port)
            if(ser.is_open != True):
                raise ConnectionError("Serial port failed to open")
            try:
                self.ser = ser
                logging.info(self.id())
                logging.info("Successfully connected to TG5012A on %s" % (serial_port))
            except:
                ser.close()
                raise
        else:
            # Open LAN connection
            self.sock = socket.socket()
            self.sock.connect((address, port))
            try:
                logging.info(self.id())
                logging.info("Successfully connected to TG5012A on %s:%d" % (address, port))
            except:
                self.sock.close()
                raise
        
    def close(self):
        """Close the serial connection."""
        self.ser.close()

    def reopen(self):
        """Reopen the serial connection."""
        self.ser.open()
        if(self.ser.is_open != True):
            raise ConnectionError("Serial port failed to open")
        logging.info("Successfully connected to %s" % (self.ser.port))
        logging.info(self.id())  

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
        valid_waveforms = ["SINE", "SQUARE", "TRIANG", "RAMP", "PULSE", "NOISE", "ARB"]
        if set not in valid_waveforms:
            raise ValueError("Invalid waveform. It should be one of %s" % (valid_waveforms))
        return self.set("WAVE", str(set))
    
    def frequency(self, set = 1):
        """Sets the output frequency in Hz"""
        return self.set("FREQ", str(set))
    
    def period(self, set = 1):
        """Sets the output period in seconds"""
        return self.set("PER", str(set))
    
    def amplitude_range(self, set = "AUTO"):
        """Sets the output amplitude range"""
        valid = ["AUTO", "HOLD"]
        if set not in valid:
            raise ValueError("Invalid amplitude range. It should be one of %s" % (valid))
        return self.set("AMPLRNG", str(set))
    
    def amplitude_unit(self, set = "VPP"):
        """Sets the output amplitude unit"""
        valid = ["VPP", "VRMS", "DBM"]
        if set not in valid:
            raise ValueError("Invalid amplitude unit. It should be one of %s" % (valid))
        return self.set("AMPUNIT", str(set))    

    def amplitude(self, set = 1):
        """Sets the output amplitude, in volts"""
        return self.set("AMPL", str(set))
        
    def offset(self, set = 0):
        """Sets the DC offset, in volts"""
        return self.set("DCOFFS", str(set))
    
    def high(self, set = 1):
        """Sets the amplitude high level, in volts"""
        return self.set("HILVL", str(set))
    
    def low(self, set = 0):
        """Sets the amplitude low level, in volts"""
        return self.set("LOLVL", str(set))
    
    def output(self, set = "ON"):
        """Sets the output on, off, normal or invert"""
        valid = ["ON", "OFF", "NORMAL", "INVERT"]
        if set not in valid:
            raise ValueError("Invalid output. It should be one of %s" % (valid))
        return self.set("OUTPUT", set)
    
    def output_load(self, set = 50):
        """Sets the output load, in Ohms"""
        if set != 'OPEN' and (set < 1 or set > 10000):
            raise ValueError("Invalid output load. It should be between 1 and 10000 or OPEN")
        return self.set("ZLOAD", str(set))

    def square_symmetry(self, set = 50):
        """Sets the square wave symmetry, in percent"""
        if set < 0 or set > 100:
            raise ValueError("Invalid square symmetry. It should be between 0 and 100")
        return self.set("SQRSYMM", str(set))
    
    def ramp_symmetry(self, set = 50):
        """Sets the ramp wave symmetry, in percent"""
        if set < 0 or set > 100:
            raise ValueError("Invalid ramp symmetry. It should be between 0 and 100")
        return self.set("RMPSYMM", str(set))
    
    def sync_output(self, set = "OFF"):
        """Sets the sync output on or off"""
        valid = ["ON", "OFF"]
        if set not in valid:
            raise ValueError("Invalid sync output. It should be one of %s" % (valid))
        return self.set("SYNCOUT", set)
    
    def sync_type(self, set = "AUTO"):
        """Sets the sync type"""
        valid = ["AUTO", "CARRIER", "MODULATION", "SWEEP", "BURST", "TRIGGER"]
        if set not in valid:
            raise ValueError("Invalid sync type. It should be one of %s" % (valid))
        return self.set("SYNCTYPE", set)
        
    def phase(self, set = 0):
        """Sets the output phase, in degrees"""
        return self.set("PHASE", str(set))
    
    def align(self):
        """Sends signal to align zero phase reference of both channels"""
        return self.set("ALIGN")
    
    # Pulse Generator Commands

    def pulse_frequency(self, set = 1):
        """Sets the pulse frequency, in Hz"""
        return self.set("PULSFREQ", str(set))
    
    def pulse_period(self, set = 1):
        """Sets the pulse period, in seconds"""
        return self.set("PULSPER", str(set))
    
    def pulse_width(self, set = 1):
        """Sets the pulse width, in seconds"""
        return self.set("PULSWID", str(set))
    
    def pulse_symmetry(self, set = 50):
        """Sets the pulse symmetry, in percent"""
        if set < 0 or set > 100:
            raise ValueError("Invalid pulse symmetry. It should be between 0 and 100")
        return self.set("PULSSYMM", str(set))
    
    def pulse_edge(self, set = 0):
        """Set the pulse waveform edges (positive and negative edge) in seconds. 
        Value zero sets to the minimum value allowed."""
        return self.set("PULSEDGE", str(set))

    def pulse_range(self, set = 1):
        """Set the pulse rise and fall range to 1, 2 or 3.
        1 - sets the range from 5ns to 99.9ns
        2 - sets the range from 100ns to 1.999us
        3 - sets the range from 2us to 40us"""
        if set not in [1,2,3]:
            raise ValueError("Invalid pulse range. It should be 1,2 or 3")
        return self.set("PULSRANGE", str(set))

    def pulse_rise(self, set = 0.001):
        """Sets the pulse rise time, in seconds"""
        return self.set("PULSRISE", str(set))
    
    def pulse_fall(self, set = 0.001):
        """Sets the pulse fall time, in seconds"""
        return self.set("PULSFALL", str(set))
    
    def pulse_delay(self, set = 0):
        """Sets the pulse delay, in seconds"""
        return self.set("PULSDLY", str(set))
    
    # Dual-channel Function Commands

    def amplitude_coupling(self, set = "ON"):
        """Sets the amplitude coupling"""
        valid = ["ON", "OFF"]
        if set not in valid:
            raise ValueError("Invalid amplitude coupling. It should be one of %s" % (valid))
        return self.set("AMPLCPLNG", set)
    
    def output_coupling(self, set = "ON"):
        """Sets the output coupling"""
        valid = ["ON", "OFF"]
        if set not in valid:
            raise ValueError("Invalid output coupling. It should be one of %s" % (valid))
        return self.set("OUTPUTCPLNG", set)
    
    def frequency_coupling(self, set = "ON"):
        """Sets the frequency coupling"""
        valid = ["ON", "OFF"]
        if set not in valid:
            raise ValueError("Invalid frequency coupling. It should be one of %s" % (valid))
        return self.set("FRQCPLSWT", set)
    
    def frequency_coupling_type(self, set = "RATIO"):
        """Sets the frequency coupling type"""
        valid = ["RATIO", "OFFSET"]
        if set not in valid:
            raise ValueError("Invalid frequency coupling type. It should be one of %s" % (valid))
        return self.set("FRQCPLTYP", set)

    def frequency_coupling_ratio(self, set = 1):
        """Sets the frequency coupling ratio"""
        return self.set("FRQCPLRAT", str(set))
    
    def frequency_coupling_offset(self, set = 0):
        """Sets the frequency coupling offset in Hz"""
        return self.set("FRQCPLOFS", str(set))
    
    def pulse_frequency_coupling(self, set = "ON"):
        """Sets the pulse frequency coupling"""
        valid = ["ON", "OFF"]
        if set not in valid:
            raise ValueError("Invalid pulse frequency coupling. It should be one of %s" % (valid))
        return self.set("PLSFRQCPLSWT", set)
    
    def pulse_frequency_coupling_type(self, set = "RATIO"):
        """Sets the pulse frequency coupling type"""
        valid = ["RATIO", "OFFSET"]
        if set not in valid:
            raise ValueError("Invalid pulse frequency coupling type. It should be one of %s" % (valid))
        return self.set("PLSFRQCPLTYP", set)
    
    def pulse_frequency_coupling_ratio(self, set = 1):
        """Sets the pulse frequency coupling ratio"""
        return self.set("PLSFRQCPLRAT", str(set))
    
    def pulse_frequency_coupling_offset(self, set = 0):
        """Sets the pulse frequency coupling offset in Hz"""
        return self.set("PLSFRQCPLOFS", str(set))
    
    def tracking(self, set = "EQUAL"):
        """Set channel tracking to OFF, EQUAL or INVERT"""
        valid = ["OFF", "EQUAL", "INVERT"]
        if set not in valid:
            raise ValueError("Invalid tracking. It should be one of %s" % (valid))
        return self.set("TRACKING", set)
    
    
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
    
    def beep(self):
        """Sounds the instrument's beeper"""
        return self.set("BEEP")
    
    def local(self):
        """Sets the instrument to local mode"""
        return self.set("LOCAL")    

    def query(self, cmd):
        self.write(cmd)
        ret = self.read()
        if cmd != "QER?" and cmd != "EER?" and self.error_check:
            err = self.query_error()
            if int(err) != 0:
                raise ValueError("Instrument returned query error %s" % (err))        
        if(self.auto_local and cmd != "LOCAL" and cmd != "QER?" and cmd != "EER?"):
            self.local()
        return ret
    
    def set(self, cmd, value=None):
        if(value is None):
            ret = self.write(cmd)
        else:
            ret = self.write(cmd + ' ' + str(value))
        if self.error_check:
            err = self.execution_error()
            if int(err) != 0:
                raise ValueError("Instrument returned execution error %s" % (err))
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