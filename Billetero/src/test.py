#!/usr/bin/env python3

from BillVal import BillVal
import BillVal as Code
import serial.tools.list_ports
import serial
import time
import logging
   
import dinUsb 
  
# TODO:_ INVESTIGAR ESTADO 23 NO ESTA DECLARADO
def main():
    (portBilletero,portMonedero) = dinUsb.checkPorts()
    bv = BillVal(str(portBilletero))
    print("Please connect bill validator.")
    bv.power_on()

    if bv.init_status == Code.POW_UP:
        logging.info("BV powered up normally.")
        
    elif bv.init_status == Code.POW_UP_BIA:
        logging.info("BV powered up with bill in acceptor.")
        
    elif bv.init_status == Code.POW_UP_BIS:
        logging.info("BV powered up with bill in stacker.")

    if bv.init_status == Code.IDLE:
        print("Setting to INHIBIT/DISABLE (enable setting buchubills)")
        
        """ # CON ESTAS LINEAS PAGAS
        print("payout")
        (status,data) = bv.req_status()
        while (status != Code.INHIBIT):
            bv.set_inhibit(0)"""

    (status,data) = bv.req_status()
  
    if  (status == Code.INHIBIT):
        print("Setting to INHIBIT/DISABLE (enable setting buchubills)")
        
        """CON ESTAS LINEAS PAGAS"""
        bv.sendRawCommand()
        
        """ #CON ESTAS LINEAS MODO GET BILLS"""
        while (status != Code.IDLE):
            bv.set_inhibit(1)        

    bv.poll()
    print("1 payout 2getBills")
    
# FC   09   F0   20   4A   01  02 // 8B   5C
# 252   9   240   32   74   1   2     139  92
def payout(bv):
    print("payout")
    (status,data) = bv.req_status()
    while (status != Code.INHIBIT):
        bv.set_inhibit(0)
    time.sleep(1)
    bv.sendRawCommand()

def getBills(bv):
    (status,data) = bv.req_status()
    while (status != Code.IDLE):
        bv.set_inhibit(1)

if __name__ == '__main__':
    main()
    