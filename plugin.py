#!/usr/bin/env python
"""
Tuyi API - Works with Poolex heatpump
"""
"""
<plugin key="TuyaAPI" name="Tuya API - Poolex Heatpump" version="0.1" author="Joerek van Gaalen">
    <params>
        <param field="Address" label="Local IP" width="200px" required="true" default="127.0.0.1"/>
        <param field="Mode1" label="Tuya ID" width="200px" required="true" default="" />
        <param field="Mode2" label="Tuya key" width="200px" required="true" default="" />
        <param field="Mode3" label="Tuya protocol" width="200px" required="true" default="3.3" />
        <param field="Mode4" label="Reading Interval (sec)" width="40px" required="true" default="60" />
    </params>
</plugin>
"""

import Domoticz
import subprocess	#For OS calls
import json

selectorMap = {'Auto': 0,
               'ECO_Heat': 10,
               'ECO_Cool': 20,
               'Boost_Heat': 30,
               'Boost_Cool': 40}

selectorMapReverse = {0: 'Auto',
                      10: 'ECO_Heat',
                      20: 'ECO_Cool',
                      30: 'Boost_Heat',
                      40: 'Boost_Cool'}

SourceOptions =  {'LevelActions': '||||',
                  'LevelNames': 'Auto|ECO_Heat|ECO_Cool|Boost_Heat|Boost_Cool',
                  'LevelOffHidden': 'false',
                  'SelectorStyle': '1'}

def proper_round(num, dec=0):
    num = str(num)[:str(num).index('.')+dec+2]
    if num[-1]>='5':
        return float(num[:-2-(not dec)]+str(int(num[-2-(not dec)])+1))
    return float(num[:-1])

def onStart():
    Domoticz.Log("Domoticz Tuya API - Poolex Heatpump plugin start")

    if len(Devices) == 0:
        Domoticz.Log("Domoticz Tuya API - Adding devices")

        Domoticz.Device(Name="Switch", Unit=1, TypeName="Switch").Create()
        Domoticz.Device(Name="SetPoint", Unit=2, Type=242, Subtype=1).Create()
        Domoticz.Device(Name="Temperature In", Unit=3, Type=80, Subtype=5).Create()
        Domoticz.Device(Name="Mode", Unit=4, TypeName="Selector Switch", Switchtype=18, Options=SourceOptions).Create()
        Domoticz.Device(Name="Unknown", Unit=21, Type=243, Subtype=31).Create()

    Domoticz.Heartbeat(int(Parameters["Mode4"]))
    
def onHeartbeat():
    try:
        res = str(subprocess.check_output(['tuya-cli', 'get', '--ip', Parameters["Address"], '--id',  Parameters["Mode1"], '--key', Parameters["Mode2"], '--protocol-version', Parameters["Mode3"]], stderr=subprocess.STDOUT))

        res = res[2:len(res) - 3]
        res = res.replace("'", "\"")
        res = res.replace("\\n", "")
        
        objects = json.loads(res)
        Domoticz.Debug("Poolex values:")
        Domoticz.Debug("Switch: " + str(objects['1']))
        Domoticz.Debug("SetPoint: " + str(objects['2']))
        Domoticz.Debug("Temp In: " + str(objects['3']))
        Domoticz.Debug("Mode: " + objects['4'])
        Domoticz.Debug("Unknown: " + str(objects['21']))

        if (objects['1'] == False and Devices[1].nValue != 0):
            Devices[1].Update(0, 'Off')
        elif (objects['1'] == True and Devices[1].nValue != 1):
            Devices[1].Update(1, 'On')
        if (str(objects['2']) != Devices[2].sValue):
            Devices[2].Update(0, str(objects['2']))
        Devices[3].Update(0, str(objects['3']))
        if (str(selectorMap[objects['4']]) != Devices[4].sValue):
            Devices[4].Update(0, str(selectorMap[objects['4']]))
        if (str(objects['21']) != Devices[21].sValue):
            Devices[21].Update(0, str(objects['21']))

    except Exception as err:
        Domoticz.Error("Tuya API Error: " + str(err))

def onCommand(Unit, Command, Level, Hue):
    try:
        if (Unit == 1):
            if (Command == 'Off'):
                status = 'false'
                Devices[1].Update(0, 'Off')
            else:
                status = 'true'
                Devices[1].Update(1, 'On')
            subprocess.check_output(['tuya-cli', 'set', '--ip', Parameters["Address"], '--id',  Parameters["Mode1"], '--key', Parameters["Mode2"], '--protocol-version', Parameters["Mode3"], '--dps', '1', '--set', status], stderr=subprocess.STDOUT)

        if (Unit == 2):
            Devices[2].Update(0, str(Level))
            SetPoint = proper_round(Level)
            subprocess.check_output(['tuya-cli', 'set', '--ip', Parameters["Address"], '--id',  Parameters["Mode1"], '--key', Parameters["Mode2"], '--protocol-version', Parameters["Mode3"], '--dps', '2', '--set', str(SetPoint)], stderr=subprocess.STDOUT)

        if (Unit == 4):
            Devices[4].Update(Level, str(Level))
            subprocess.check_output(['tuya-cli', 'set', '--ip', Parameters["Address"], '--id',  Parameters["Mode1"], '--key', Parameters["Mode2"], '--protocol-version', Parameters["Mode3"], '--dps', '4', '--set', '\'' + str(selectorMapReverse[Level]) + '\''], stderr=subprocess.STDOUT)

    except Exception as err:
        Domoticz.Error("Tuya API Error: " + str(err))
