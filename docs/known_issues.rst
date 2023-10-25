Gyger SMLD micro valves
+++++++++++++++++++++++
To trigger valves you need to send them a pulse longer than 10 us.

Duplicate COM ports under Windows
++++++++++++++++++++++++++++++++++
Windows sometimes assigns two different devices to the same COM port (e.g. `[1] <https://superuser.com/questions/1587613/windows-10-two-serial-usb-devices-were-given-an-identical-port-number>`_, 
`[2] <https://answers.microsoft.com/en-us/windows/forum/all/com-port-changes-and-same-for-two-devices-after/84837db6-2ef3-4fa6-9568-47e8805bd290>`_). 
This makes communication with the devices impossible using the COM port. The workaround is to manually change the COM port assigned.

Open Device manager and right click on start button and then on Device manager.
Expand port "COMS & LPT".
Right click on problematic device and then on properties.
Go to port settings and click on Advanced.
You will be able to make the changes on this screen.