# SheetJet
[![docs workflow](https://github.com/FilipeMaia/sheetjet/actions/workflows/documentation.yml/badge.svg)](https://filipemaia.github.io/sheetjet/)

SheetJet is a python package to control hardware devices necessary to run a sheet jet sample delivery experiment, like the one described in [https://doi.org/10.1107/S2052252523007972](https://doi.org/10.1107/S2052252523007972)

It currently controls:
-  Fritz Gyger AG SMLD micro valves, using the serial interface to VC Mini
- Rheodyne MXII valve from IDEX Health & Science
- TG5012A function generator from Aim-TTi to trigger the micro valves

## Installation

To install it simply run `pip install .` inside the source directory, like any python package.

## Documentation

[https://filipemaia.github.io/sheetjet/](https://filipemaia.github.io/sheetjet/)

## Usage

Here's an example of how to use the package:

```python
import sheetjet

# Find out the serial ports of the different devices.
# The names are arbitrary strings just to identify each device.
# You will need to disconnect/connect each of the devices
# to identify their ports. If you already know the port 
# names you can skip this step.
devices = sheetjet.discover(['micro_valve','func_gen'])

# Initialize the devices
vcmini = sheetjet.VCMini(serial_port=devices['micro_valve'].device)
func_gen = sheetjet.TG5012A(serial_port=devices['func_gen'].device)

# If we already know the serial port to an MXII valve
valve = sheetjet.MXII(serial_port='COM7')

# You can start to interact with them
print(func_gen.id())
func_gen.channel(2)
print(func_gen.channel())
func_gen.channel(1)
print(func_gen.channel())

print(vcmini.address())
print(vcmini.address(1))
print(vcmini.address())

print(valve.port())


```

## Known Issues

### Gyger SMLD micro valves

To trigger valves you need to send them a pulse longer than 10 us.

### Duplicate COM ports under Windows

Windows sometimes assigns two different devices to the same COM port (e.g. [1](https://superuser.com/questions/1587613/windows-10-two-serial-usb-devices-were-given-an-identical-port-number), [2](https://answers.microsoft.com/en-us/windows/forum/all/com-port-changes-and-same-for-two-devices-after/84837db6-2ef3-4fa6-9568-47e8805bd290)). This makes communication with the devices impossible using the COM port.
The workaround is to manually change the COM port assigned.
1. Open Device manager and right click on start button
and then on Device manager.
2. Expand port "COMS & LPT".
3. Right click on problematic device and then on properties.
4. Go to port settings and click on Advanced.
5. You will be able to make the changes on this screen.

