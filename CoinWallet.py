# -*- coding: utf-8 -*-
"""
 @Author: Daniel Burruchaga Sola
        @Date: 25-04-22
 
Example:


Todo:
    * Review some doc and 
    * Review Feature auto-select port


|--------coinWallet------|
|        __init__     setup()    
|                     reset()
|                     tubeStatus()
|                     poll()
|                     coinType()
|                     dispense()
|                     enableInsertCoins()
|                         |
|-------------------------|

"""

import BuchuSerial  

class CoinWallet():
    # initialize the  connection to the com port
    def __init__(self):
        self.conn = BuchuSerial.BuchuSerial()
    def setup(self): # 0x09 
        command = bytearray([0x09])
        response = self.conn.serialSend(command)
#       print(response)
        return response
    def reset(self): # 0x08
        command = bytearray([0x08])
        response = self.conn.serialSend(command)
#       print(response)
        return response
    def tubeStatus(self):  # 0x0A
        command = bytearray([0x0A])
        response = self.conn.serialSend(command)
#       print(response)
        return response
    def poll(self):  # 0x0B
        command = bytearray([0x0B])
        response = self.conn.serialSend(command)
#       print(response)
        return response
    def coinType(self):  # 0x0C
        command = bytearray([0x0C])
        response = self.conn.serialSend(command)
#       print(response)
        return response
    def dispense(self): # 0D
        command = bytearray([0x09])
        response = self.conn.serialSend(command)
#       print(response)
        return response
    #Enable all insert coins
    def enableInsertCoins(self): 
        command = bytearray([0x0C, 0xff, 0xff, 0xff, 0xff ])
        response = self.conn.serialSend(command)
#       print(response)
        return response
        
cW = CoinWallet()
print(cW.setup())

