# Packet dropper by IP
This program blocks your selected traffic from your selected IP.

Enable to control:
 - inbound/outbound packets
 - TCP/UDP protocol

**Download** -> https://github.com/aBT06yc/lagswitch/releases/tag/v0.2.2

‼️ **Administrator rights are REQUIRED** for the program to work (windivert inside project)

*Currently, traffic from the local network is ignored by the sniffer, if you need  to change it in the file. `connection.py` -> `ip_sniff(filter_local_ips=False)`*.
*Currently, there is no indicator in the program that would clearly indicate that you are blocking traffic by pressing a key at the moment. Therefore, I recommend using HOLD mode, also do not forget that you can change the stop traffic button, by default it is "x"*.


***if you need to build project ot .exe run this command:***

`pyinstaller --onefile --uac-admin --noconsole interface.py --name "LagSwitch Pro"`
