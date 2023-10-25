import serial.tools.list_ports as list_ports
import configparser
import logging



def discover(devices = ['VCMini', 'TG5012A', 'MXP7970', 'MXP9900'], config_file = 'sheetjet.ini', save_config = True, load_config = True):
    """
    Find the addresses of the specified devices by either 
    loading them from a configuration file or by 
    manually unplugging and plugging in the device.
    
    Parameters
    ----------
    devices: list of str
        Names of the devices to search for. 
        These are arbitrary strings that are just used to identify the devices to the user.

    config_file: str
        Path to the configuration file to load and save the device addresses to.

    save_config: bool
        If True, save the addresses of the devices found to the configuration file.

    load_config: bool
        If True, load the addresses of the devices from the configuration file instead of searching for them again.

    Returns
    -------
    dict
        A dictionary with the ``DeviceInfo`` of each of the devices specified.
    
    See Also
    --------
    sheetjet.DeviceInfo

    """
    ret = None
    if(load_config):
        ret = read_config(config_file)
        if ret is not None:
            found_all = True
            for d in devices:
                if d not in ret or ret[d] is None:
                    found_all = False
                    break
            if found_all:
                return ret
        
    print('Performing manual USB address search.')
    if ret is None:
        ret = {}
    for d in devices:
        if d not in ret or ret[d] is None:
            ret[d] = discover_device(d)
    if save_config:
        write_config(ret, config_file)
    return ret

def discover_device(name):
    print('Searching for %s' % (name))
    input('    Unplug the USB/Serial cable connected to %s. Press Enter when unplugged...' %(name))
    before = list_ports.comports()
    check_duplicate_ports(before)
    logging.debug('Devices found after unplugging:\n%s' %(format_devices_found(before)))
    input('    Reconnect the cable. Press Enter when the cable has been plugged in...')
    after = list_ports.comports()
    check_duplicate_ports(after)
    logging.debug('Devices found after replugging:\n%s' %(format_devices_found(after)))
    port = [i for i in after if i not in before]
    if(len(port) == 1):
        return DeviceInfo(port[0].device, port[0].hwid)
    elif(len(port) == 0):
        raise ConnectionError('No device found.')
    
    if(len(port) != 1):
        raise ConnectionError('Multiple devices changed!')
    return None

def format_devices_found(comports):
    ret = ''
    for p in comports:
        ret += "device:%s hwid:%s\n" % (p.device, p.hwid)
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
    if(config.sections() == []):
        # Got empty config
        return None
    ret = {}
    for d in config.sections():
        ret[d] = DeviceInfo.from_config(config[d]) 

    if(check_against_ports is False):
        return ret
    
    ports = list_ports.comports()
    check_duplicate_ports(ports)
    for d in ret.keys():
        found = False
        for p in ports:
            if(p.hwid == ret[d].hwid):
                logging.debug('Found %s with hwid %s at %s' %(d, p.hwid, p.device))
                found = True
                continue
        if found == False:
            logging.warning('Could not find %s with hwid %s' %(d, ret[d].hwid))
            ret[d] = None
    return ret

def check_duplicate_ports(port_list):
    devices = [p.device for p in port_list]
    repeat_devices = [i for i, x in enumerate(devices) if devices.count(x) > 1]
    if len(repeat_devices) > 0:
        logging.warning('Found repeated device names:')
        for i in repeat_devices:
            logging.warning('device:%s hwid:%s' % (port_list[i].device, port_list[i].hwid))
        logging.warning('Check https://filipemaia.github.io/sheetjet/known_issues.html#duplicate-com-ports-under-windows for a workaround.')



class DeviceInfo:
    """
    Stores basic information about a serial port and the hardware attached to it.
    This information is derived from pySerial's ``ListPortInfo`` class.
    https://pyserial.readthedocs.io/en/latest/tools.html#serial.tools.list_ports.ListPortInfo

    Attributes
    ----------
    device : str
        The device name/path, e.g. ``COM4`` on Windows or ``/dev/ttyUSB0`` under Linux.
        Corresponds to the ``device`` attribute in ``ListPortInfo``.
    hwid : str
        An identifier for the hardware attached on the device.
        Should help us to later identify if the same hardware is still plugged in.
    
    """
    def __init__(self, device, hwid):
        self.device = device
        self.hwid = hwid
    
    @classmethod
    def from_config(cls, config):
        if all(k in config for k in ('device', 'hwid')):
            return cls(config['device'], config['hwid'])
        else:
            return None
    
    def __str__(self):
        return 'device=%s hwid=%s' % (self.device, self.hwid)

    def __repr__(self):
        return 'DeviceInfo(device=%s, hwid=%s)' % (self.device, self.hwid)