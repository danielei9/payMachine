# -*- coding: utf-8 -*-
"""
 @Author: Daniel Burruchaga Sola
        @Date: 25-04-22
 
Example:


Todo:
    * Review some doc and 
    * Feature auto-select port

"""

import BuchuSerial  

def coinWallet():
    # initialize the  connection to the com port
   
    conn = BuchuSerial()
    def setup(): # 0x09 
        command = bytearray([0x09])
        conn.serialSend(command)
    def reset(): # 0x08
        command = bytearray([0x08])
        conn.serialSend(command)
    def tubeStatus():  # 0x0A
        command = bytearray([0x0A])
        conn.serialSend(command)
    def poll():  # 0x0B
        command = bytearray([0x0B])
        conn.serialSend(command)
    def coinType():  # 0x0C
        command = bytearray([0x0C])
        conn.serialSend(command)
    def dispense(): # 0D
        command = bytearray([0x09])
        conn.serialSend(command)
    #Enable all insert coins
    def enableInsertCoins(): 
        command = bytearray([0x0C, 0xff, 0xff, 0xff, 0xff ])
        conn.serialSend(command)
