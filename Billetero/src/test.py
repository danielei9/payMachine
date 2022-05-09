#!/usr/bin/env python3

from BillVal import BillVal
import BillVal as Code
import serial.tools.list_ports
import serial
import time
import logging


def main():
    port = '/dev/ttyUSB0'  # JCM UAC device (USB serial adapter)
#     port = 'COM31'  # JCM UAC device (USB serial adapter)
    
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
        #Con esto podemos cambiar de estado de IDLE a dar billetes
        print("Setting to INHIBIT/DISABLE (enable setting buchubills)")
        bv.payout()
    (status,data) = bv.req_status()
    """
        #Con esto podemos cambiar de estado de recoger billetes a dar billetes
        if  status == Code.INHIBIT:
        print("Setting to INHIBIT/DISABLE (enable setting buchubills)")
        bv.set_inhibit(1)
    """

    bv.poll()
# FC   09   F0   20   4A   01  02 // 8B   5C
# 252   9   240   32   74   1   2     139  92
    

if __name__ == '__main__':
    main()
