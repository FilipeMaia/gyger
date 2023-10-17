import serial.tools.list_ports as list_ports
import configparser
import logging



def discover(config_file = 'sheetjet.ini', save_config = True, load_config = True):
    """
    Find the addresses of all the serial device by either 
    loading them from a configuration file or by 
    manually unplugging and plugging in the device.
    
    Returns:
    Dictionary with the device name of each of the 3 
    devices: VCMini, TG5012A and MXII
    """
    ret = None
    if(load_config):
        ret = read_config(config_file)
        if None not in ret.values():
            return ret
        
    print('Performing manual USB address search.')
    if ret is None:
        ret = {}
    for d in ['VCMini', 'TG5012A', 'MXII']:
        if d not in ret or ret[d] is None:
            ret[d] = discover_device(d)
    if save_config:
        write_config(ret, config_file)
    return ret

def write_config(devices, config_file):
    config = configparser.ConfigParser()
    for d in devices:
        config[d] = devices[d].__dict__
    with open(config_file, 'w') as configfile:
        config.write(configfile)


def read_config(config_file, check_against_ports = True):
    config = configparser.ConfigParser()
    try:
        config.read(config_file)
    except:
        logging.warning('Could not read config file %s' %(config_file))
        return None
    ret = {}
    for d in config:
        ret[d] = DeviceInfo.from_config(config[d]) 

    if(check_against_ports is False):
        return ret
    
    ports = list_ports.comports()
    for d in ['VCMini', 'TG5012A', 'MXII']:
        found = False
        for p in ports:
            if(p.serial_number == ret[d].serial_number):
                logging.debug('Found %s with serial_number %s and hwid %s at %s' %(d, p.serial_number, p.hwid, p.device))
                found = True
                continue
        if found == False:
            logging.warning('Could not find %s with serial_number %s and hwid %s' %(d, ret[d].serial_number, ret[d].hwid))
            config[d] = None
    return config

def discover_device(name):
    print('Searching for %s' % (name))
    input('    Unplug the USB/Serial cable connected to %s. Press Enter when unplugged...' %(name))
    before = list_ports.comports()
    input('    Reconnect the cable. Press Enter when the cable has been plugged in...')
    after = list_ports.comports()
    port = [i for i in after if i not in before]
    if(len(port) == 1):
        return DeviceInfo(port[0].device, port[0].hwid, port[0].serial_number)
    elif(len(port) == 0):
        raise ConnectionError('No device found.')
    
    if(len(port) != 1):
        raise ConnectionError('Multiple devices changed!')
    return None

class DeviceInfo:
    def __init__(self, device, hwid, serial_number):
        self.device = device
        self.hwid = hwid
        self.serial_number = serial_number
    
    @classmethod
    def from_config(cls, config):
        return cls(config['device'], config['hwid'], config['serial_number'])