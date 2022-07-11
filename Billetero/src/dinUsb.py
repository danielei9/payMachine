import os
from os.path import join
# MONEDERO idvendor  067b

def find_tty_usb(idVendor, idProduct):
    for dnbase in os.listdir('/sys/bus/usb/devices'):
        dn = join('/sys/bus/usb/devices', dnbase)
#         print(dn)
        if not os.path.exists(join(dn, 'idVendor')):
            continue
        idv = open(join(dn, 'idVendor')).read().strip()
#         print(idv)
        if idv != idVendor:
            continue
        idp = open(join(dn, 'idProduct')).read().strip()
#         print(idp)
        if idp != idProduct:
            continue
        for subdir in os.listdir(dn):
            if subdir.startswith(dnbase+':'):
                for subsubdir in os.listdir(join(dn, subdir)):
                    if subsubdir.startswith('ttyUSB'):
                        return join('/dev', subsubdir)

import re
import subprocess
def checkPorts():
    devices = []
    portBilletero = ""
    portMonedero = ""
    
    device_re = re.compile("Bus\s+(?P<bus>\d+)\s+Device\s+(?P<device>\d+).+ID\s(?P<id>\w+:\w+)\s(?P<tag>.+)$", re.I)
    df = subprocess.check_output("lsusb")    
    df = str(df)
    df = df.replace("b'", '')
    for i in df.split("\\n"):
        if i:
            info = device_re.match(i)
            if info:
                dinfo = info.groupdict()
                dinfo['device'] = '/dev/bus/usb/%s/%s' % (dinfo.pop('bus'), dinfo.pop('device'))
                devices.append(dinfo)
#     print (devices)

    for device in devices:
        idUsb = str(device['id']).split(':')
        a = str(idUsb[0])
        b = str(idUsb[1])
    #     BILLETERO
        if(device['id'] == "067b:2303"):
            portBilletero = find_tty_usb(a,b)
            print("BILLETERO: ",portBilletero)
        if(device['id'] == "0403:6001"):
    #     MONEDERO
            portMonedero = find_tty_usb(a,b) 
            print("MONEDERO: ",portMonedero)
    return portBilletero,portMonedero

# portBilletero,portMonedero = checkPorts()
# print(portBilletero,portMonedero)