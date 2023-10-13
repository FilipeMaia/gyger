"""Control of the Aim TTi TG5012A function generator."""

import socket

class TG5012A:
    def __init__(self, address='tg5012a.local', port=9221):
        self.terminator = b'\n'
        self.sock = socket.socket()
        self.sock.connect((address, port))
        print("Successfully connected to %s:%d" % (address, port))
        print(self.id())

        
    def query(self, cmd):
        self.sock.send(cmd.encode('ascii') + self.terminator)
        recv = self.sock.recv(1024)
        return recv.decode('ascii').strip()
    
    def id(self):
        """Returns the ID string of the instrument"""
        return self.query("*IDN?")
