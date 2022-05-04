#!/usr/bin/env python3

from id003 import BillVal
import id003 as Code
import serial.tools.list_ports
import serial
import time
import logging


def main():
    port = '/dev/ttyUSB0'  # JCM UAC device (USB serial adapter)
    
    bv = BillVal(port)
    print("Please connect bill validator.")
    bv.power_on()
    
    if bv.init_status == Code.POW_UP:
        logging.info("BV powered up normally.")
    elif bv.init_status == Code.POW_UP_BIA:
        logging.info("BV powered up with bill in acceptor.")
    elif bv.init_status == Code.POW_UP_BIS:
        logging.info("BV powered up with bill in stacker.")
    
    if bv.init_status == Code.IDLE:
        print("hola")
        bv.buchu_set_recycler_config()
#         bv.buchu_set_inhibit()

#     bv.buchu_set_inhibit()
    bv.poll()
#     bv.send_command(195,[0x00])
#     bv.send_command(195,bytes([0x00]))
#     bv.send_command([240, 32],bytes([0x20,0x4A,0x01,0x02])) 
# FC   09   F0   20   4A   01  02 // 8B   5C
# 252   9   240   32   74   1   2     139  92
    

if __name__ == '__main__':
    main()
