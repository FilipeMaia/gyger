import logging
import serial

class MXII:
    """
    Control of IDEX HS MX Series II valves.

    Based on the manuals found at https://www.idex-hs.com/docs/default-source/product-manuals/mx-series-ii-driver-development-package.pdf.zip
    and https://www.idex-hs.com/docs/default-source/product-manuals/rheolink-i2c-communication-protocol-for-titanex.pdf.zip
    """
    def __init__(self, serial_port = None, baudrate = 19200, timeout_s = 1):
        # Open communication with valve controller VC-Mini
        ser = serial.Serial(port = serial_port, baudrate = baudrate, timeout = timeout_s)      
        if(ser.is_open != True):
            raise ConnectionError("Serial port failed to open")
        self.ser = ser
        self.terminator = '\r'
        # Test one command
        try:
            self.mode()
            logging.info("Successfully connected to MX II on %s" % (serial_port))
        except:
            ser.close()
            raise

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
        # Test one command
        self.mode()
        logging.info("Successfully connected to MX II on %s" % (self.ser.port))

    def port(self, port = None):
        """Queries or sets the active port"""
        if(port is None):
            # The valve returns the port number in hex
            ret = int(self.query("S"), 16)
            if ret > 16:
                logging.warning("valve failure error %d" % (ret))
            return ret
        if(port < 1 or port > 16):
            raise ValueError("Port must be between 1 and 16")
        return self.write("P%02X" % (port))
    
    def home(self):
        """Homes the valve"""
        return self.write("M00")
    
    def mode(self, set=None):
        if(set is None):
            ret = int(self.query("D00"), 16)
            return ret
        else:
            raise NotImplementedError("Setting the mode is not implemented yet")
    
    def query(self, cmd):
        """Queries the valve controller"""
        self.write(cmd)
        return self.ser.read_until(self.terminator).decode('ascii').strip()

    def write(self, cmd):
        """Writes a command to the valve controller"""
        return self.ser.write((cmd + self.terminator).encode('ascii'))
    

    

