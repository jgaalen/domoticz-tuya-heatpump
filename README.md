# domoticz-tuya-heatpump
Domoticz plugin for Tuya (W'eau) Heatpumps
This plugin reads the values from you Heatpump and gives you the ability to start/stop it, set a temperature.
It needs the [tuya-cli](https://github.com/TuyaAPI/cli). Make sure you have the id and key of the heatpump by following [a these](https://github.com/codetheweb/tuyapi/blob/master/docs/SETUP.md) steps.

## Installation
From your domoticz home directory:
```
cd plugins
git clone https://github.com/jgaalen/domoticz-tuya-heatpump.git
npm i @tuyapi/cli -g
systemctl restart domoticz
```

## Tested on
- W'eau heatpump

Not sure if other Tuya heatpumps are supported


