# SheetJet

SheetJet is a python package to control hardware devices necessary to run a sheet jet sample delivery experiment, like the one described in [https://doi.org/10.1107/S2052252523007972](https://doi.org/10.1107/S2052252523007972)

It currently controls:
-  two Fritz Gyger AG SMLD micro valves, using the serial interface to VC Mini
- a Rheodyne MXII valve from IDEX Health & Science
- a TG5012A function generator from Aim-TTi to trigger the micro valves

## Installation

To install it simply run `pip install .` inside the source directory, like any python package.

## Usage

Here's an example of how to use the package:

```python
import sheetjet

# Find out the serial ports of the different devices
# You will need to disconnect/connect each of the devices
# to identify their ports. If you already know the port 
# names you can skip this step 
devices = sheetjet.discover()

# Initialize the devices
vcmini = sheetjet.VCMini(serial_port=devices['VCMini'].device)
func_gen = sheetjet.TG5012A(serial_port=devices['TG5012A'].device)
mxii = sheetjet.MXII(serial_port=devices['MXII'].device)

# You can start to interact with them
print(func_gen.id())
func_gen.set('CHN','2')
print(func_gen.query('CHN?'))
func_gen.set('CHN','1')
print(func_gen.query('CHN?'))


print(vcmini.address())
print(vcmini.address(set=1))
print(vcmini.address())

```
