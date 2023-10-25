Known Issues
============

Gyger SMLD micro valves
+++++++++++++++++++++++
To trigger valves you need to send them a pulse longer than 10 us.

Duplicate COM ports under Windows
++++++++++++++++++++++++++++++++++
Windows sometimes assigns two different devices to the same COM port (e.g. 1, 2). This makes communication with the devices impossible using the COM port. The workaround is to manually change the COM port assigned.

Open Device manager and right click on start button and then on Device manager.
Expand port "COMS & LPT".
Right click on problematic device and then on properties.
Go to port settings and click on Advanced.
You will be able to make the changes on this screen.