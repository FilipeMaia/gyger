"""Control of the Aim TTi TG5012A function generator."""

import socket
import serial

class TG5012A:
    def __init__(self, serial_port = None, address='t539639.local', port=9221, auto_local=True):
        self.terminator = b'\n'
        self.ser = None
        self.sock = None
        if serial_port is not None:
            # Prefer serial over LAN communication        
            ser = serial.Serial(port = serial_port)
            ser.open()
            self.ser = ser
            print("Successfully connected to %s" % (serial_port))            
        else:
            # Open LAN connection
            self.sock = socket.socket()
            self.sock.connect((address, port))
            self.auto_local = auto_local
            print("Successfully connected to %s:%d" % (address, port))
        print(self.id())

        
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
            ret = self.write(cmd + ' ' + value)  
        if(self.auto_local and cmd != "LOCAL"):
            self.local()        
        return ret
    
    def id(self):
        """Returns the ID string of the instrument"""
        return self.query("*IDN?")
    
    def wait_for_completion(self):
        """Waits for the instrument to complete its tasks"""
        return self.query("*OPC?")
    
    def local(self):
        """Sets the instrument to local mode"""
        return self.set("LOCAL")
    
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