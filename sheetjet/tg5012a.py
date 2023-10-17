"""Control of the Aim TTi TG5012A function generator."""

import socket

class TG5012A:
    def __init__(self, address='t539639.local', port=9221, auto_local=True):
        self.terminator = b'\n'
        self.sock = socket.socket()
        self.sock.connect((address, port))
        self.auto_local = auto_local
        print("Successfully connected to %s:%d" % (address, port))
        print(self.id())

        
    def query(self, cmd):
        self.sock.send(cmd.encode('ascii') + self.terminator)
        recv = self.sock.recv(1024)
        ret = recv.decode('ascii').strip()
        if(self.auto_local and cmd != "LOCAL"):
            self.local()
        return ret
    
    def set(self, cmd, value=None):
        if(value is None):
            ret = self.sock.send(cmd.encode('ascii') + self.terminator)   
        else:
            ret = self.sock.send(cmd.encode('ascii') + b' ' + value.encode('ascii') + self.terminator)  
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