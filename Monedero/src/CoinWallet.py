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
|    __sendCommand    tubeStatus()
|                     poll()
|                     coinType()
|                     dispense()
|                     enableInsertCoins()
|                         |
|-------------------------|

"""
import multiprocessing
import BuchuSerial,   time
# # # # # # # # # # # # # # # # # # # # # 
# NORMAL COMMANDS
# # # # # # # # # # # # # # # # # # # # #

# RECEIVING COINS

UN_EURO = '08 54'
DOS_EURO = '08 55'
ZERO_ZERO_FIVE = '08 50'
ZERO_TEN = '08 51'
ZERO_TWNTY = '08 52'
ZERO_FIVETY = '08 53'

"""
    #Send info about setup initi
    # Response 23 bytes z1-z23
    # z1 Changer Feature Level // Level3 = 0x03 // Level2 = 0x02 ...
    #  z2-z3 country code  for the Euro is 1978 (Z2 = 19 and Z3 = 78).
    # Z4 = Coin Scaling Factor - 1 byte 
    # Z5 = Decimal Places - 1 byte 
 Indicates the number of decimal places on a credit display. For example, this could be set to 02H in the USA.
    # Z6-Z7 Coin Type Routing - 2 bytes
    # Bit is set to indicate a coin type can be routed to the tube. Valid coin types are 0 to 15.
    # Z8 - Z23 = Coin Type Credit - 16 bytes 
    # Indicates the value of coin types 0 to 15. Values must be sent in ascending order. This number is the coin's monetary value
    #  divided by the coin scaling factor. Unused coin types are sent as 00H. Unsent coin types are assumed to be zero. It is not
    # necessary to send all coin types. Coin type credits sent as FFH are assumed to be vend tokens. That is, their value is assumed to worth one vend.
"""
SETUP = [0x09]
"""

    # This command is the vehicle that the VMC should use to tell the changer that it should return to its default operating mode
"""
RESET = [0x08]
"""
    # Z1 - Z2 = Tube Full Status - 2 bytes 
Indicates status of coin tube for coin types 0 to 15. 
A bit is set to indicate a full tube. For example, bit 7 = set would
    # indicate the tube for coin type 7 is ful
    # Z3 - Z18 = Tube Status - 16 bytes Indicates the greatest number of coins that the changer “knows” definitely are present in the coin tubes.
"""
TUBE_STATUS = [0x0A]

DIAGNOSTIC_STATUS = [0x0F,0x05]
"""
    # Z1 - Z16 = Changer Activity - 16 bytes 
Indicates the changer activity. If there is nothing to report, the changer should send only an ACK. Otherwise, the only valid
    # responses 
"""
    
POLL =  [0x0B]
"""
# To enable desired coin acceptance and disable manual coin payout if desired
"""
COINTYPE = [0x0C]
DISPENSE =[0x0D]
EXPANSION_COMMAND = [0x0F]

# # # # # # # # # # # # # # # # # # # # # 
# #  EXPANSION LEVEL SUBCOMANDS
# # # # # # # # # # # # # # # # # # # # # 

IDENTIFICATION = [0x00]
PAYOUT = [0x02]
PAYOUT_STATUS = [0x03]
PAYOUT_VALUE_POLL = [0x04]
DIAGNOSTIC_STATUS = [0x05]

class CoinWallet():
    statusDeactiveThread = False
    incommingCoin = ''
    status = ''
    data = ''
    # initialize the  connection to the com port
    """-------------------------- COINWALLET() ------------------------------"""
    """-------------------------- PRIVATE FUNCTIONS ------------------------------"""
    """-------------------------- Constructor ------------------------------"""
    def __init__(self, cb):
        self.proc = multiprocessing.Process(target=self.threadReceived, args=())
        self.proc.daemon = True
        self.conn = BuchuSerial.BuchuSerial()
        self.cw_events = {
            DOS_EURO: self.__onInserted2Euro,
            UN_EURO: self.__onInsertedEuro,
            ZERO_FIVETY: self.__onInserted50Cent,
            ZERO_TWNTY: self.__onInserted20Cent,
            ZERO_TEN: self.__onInserted10Cent,
            ZERO_ZERO_FIVE: self.__onInserted05Cent,
        }
        self.cb = cb

    """-------------------------- EVENTS ------------------------------"""
   
    def __onInserted05Cent(self,data):
        if(self.data[0] == '50'  ):
            print("0.05 euro")
            self.cb(0.05)
            
    def __onInserted10Cent(self,data):
        if(self.data[0] == '51'  ):
            print("0.10 euro")
            self.cb(0.10)
            
    def __onInserted20Cent(self,data):
        if(self.data[0] == '52'  ):
            print("0.20 euro")
            self.cb(0.2)

    def __onInserted50Cent(self,data):
        if(self.data[0] == '53'  ):
            print("0.50 euro")
            self.cb(0.5)

    def __onInsertedEuro(self,data):
        if(self.data[0] == '54'):
            print("1 euro")
            self.cb(1)

    def __onInserted2Euro(self,data):
        if(self.data[0] == '55'  ):
            print("2 euros")
            self.cb(2)

    # # # # # # # # # # # # # # # # # # # # # # 
   
    """--------------------------send command ------------------------------"""
    def __sendCommand(self,command):
        response = self.conn.serialSend(bytearray(command))
        return response
    """------------------ send command and receive --------------------------"""
    def __sendCommandAndReceive(self,command):
        response = self.conn.serialSendAndReceive(bytearray(command))
        return response
    """---------------------------- ParseBytes ------------------------------"""
    def __parseBytes(self,received):
        status = str(received)[2:4]
        data = str(received)[5:(len(str(received))-5)]
        self.status = status.split(" ")
        self.data = data.split(" ")
        self.incommingCoin = str(self.status[0] + " " + self.data[0])
        if(self.incommingCoin  in self.cw_events):
            self.cw_events[self.incommingCoin ](data)
    
    """--------------------------fullTube------------------------------"""
    def __fullTube(self,tube):
        print("FULL TUBE Number " + str(tube))
        
    """--------------------------cashBack------------------------------"""
    def __cashBack(self,moneyBack):
        """
            CashBack(R) Esta función sirve
            para devolver el dinero indicado por parámetros
        """
        countCoins = moneyBack / 0.05
        return self.__sendCommand([0x0F, 0x02, int(countCoins) ])
    """-------------------------- PUBLIC FUNCTIONS ------------------------------"""
    
    """-------------------------- startThreadReceived ------------------------------"""
    def threadReceived(self):
        while not self.statusDeactiveThread:
            received = self.conn.serialReadLine()
            self.__parseBytes(received)
            print("status = " + str(self.status))
            print("data = " + str(self.data))
            self.data = str(self.data)
            status= str(self.status)

    """-------------------------- SETUP ------------------------------"""
    def setup(self): 
        return self.__sendCommand(SETUP)
    
    """-------------------------- Reset ------------------------------"""
    def reset(self): 
        return self.__sendCommand(RESET)
    
    """-------------------------- tubeStatus ------------------------------"""
    def tubeStatus(self):  
        """
        VMC Command Code Changer Response Data
        TUBE STATUS 0AH 18 bytes: Z1 - Z18
        Z1 - Z2 = Tube Full Status - 2 bytes
        Indicates status of coin tube for coin types 0 to 15.
        b15 b14 b13 b12 b11 b10 b9 b8 | b7 b6 b5 b4 b3 b2 b1 b0
         Z1 Z2
        A bit is set to indicate a full tube. For example, bit 7 = set would
        indicate the tube for coin type 7 is full.
        Z3 - Z18 = Tube Status - 16 bytes
        Indicates the greatest number of coins that the changer “knows”
        definitely are present in the coin tubes. A bytes position in the
        16 byte string indicates the number of coins in a tube for a 
        Multi-Drop Bus / Internal Communication Protocol
        MDB/ICP Version 4.3 July, 2019 5•6
        particular coin type. For example, the first byte sent indicates
        the number of coins in a tube for coin type 0. Unsent bytes are
        assumed to be zero. For tube counts greater than 255, counts
        should remain at 255. 

        """
        return self.__sendCommandAndReceive([0x0A])

        
    """-------------------------- poll ------------------------------"""
    """ NOT IN USE SUST BY THREAD """
    def poll(self):  # 0x0B
        interval = 0.2
        while True:
            poll_start = time.time()
            response = self.__sendCommand([0x0B])
            print (response)
#             self.cw_events[status](data)
#             self.bv_status = (status, data)
            wait = interval - (time.time() - poll_start)
            if wait > 0.0:
                time.sleep(wait)
        
    """-------------------------- EnableInsertCoins ------------------------------"""
    def coinType(self):  # 0x0C
        """
        Y1 - Y2 = Coin Enable - 2 bytes
        b15 b14 b13 b12 b11 b10 b9 b8 | b7 b6 b5 b4 b3 b2 b1 b0
        Y1 Y2
        A bit is set to indicate a coin type is accepted. For example, bit 6 is set to
        indicate coin type 6, bit 15 is set to indicate coin type 15, and so on. To
        disable the changer, disable all coin types by sending a data block containing
        0000H. All coins are automatically disabled upon reset.
        Y3 - Y4 = Manual Dispense Enable - 2 bytes
        b15 b14 b13 b12 b11 b10 b9 b8 | b7 b6 b5 b4 b3 b2 b1 b0
        Y3 Y4
        A bit is set to indicate dispense enable. For example, bit 2 is set to enable
        dispensing of coin type 2. This command enables/disables manual
        dispensing using optional inventory switches. All manual dispensing switches
        are automatically enabled upon reset. 
        """
        return self.__sendCommand([0x0C])
    
    """-------------------------- Dispense ------------------------------"""
    """  NOT IN USE """
    def dispense(self): # 0D
        return self.__sendCommand([0x0D,0x05])
    
    """-------------------------- EnableInsertCoins ------------------------------"""
    def enableInsertCoins(self):
        """
            This function enable the possibility
            of insert all kind of coins
        """
        return self.__sendCommand([0x0C, 0xff, 0xff, 0xff, 0xff])

    """--------------------------cashBack------------------------------"""
    def cashBackRoutine(self,moneyBack):
        """
            CashBack(R) Esta función sirve
            para devolver el dinero indicado por parámetros
            realizando la rutina completa
        """
        self.reset()
        time.sleep(0.5)
        self.setup()
        self.enableInsertCoins()
        self.tubeStatus()
        return self.__cashBack(moneyBack)
    """--------------------------startReceivingMode------------------------------"""
    def startReceivingMode(self):
        """
            This function start the service
        """
        self.proc.start()
        self.enableInsertCoins()
        self.cb("start")
    """--------------------------stopReceivingMode------------------------------"""
    def stopReceivingMode(self):
        """
            This function stop the service
        """
#         self.proc.join()
        self.proc.close()
        self.statusDeactiveThread = True

# 
# if __name__=='__main__':
#     cW = CoinWallet()
#     time.sleep(1)
#     cW.reset()
#     cW.setup()
# #     cW.startReceivingMode()
#     time.sleep(2)
#     cW.enableInsertCoins()
#     time.sleep(2)
# #     print(cW.cashBackRoutine(0.85))
# 
#     while True:
#         s_r = ''
#         while s_r not in ('1', '2', '3','4','4','5' ,'r'):
#             s_r = input(    "(1) Mode Input Coin (Polling and denoms)\n"
#                             "(2) Mode PayOut (add space and quantity) \n"
#                             "(3) RESET MACHINE \n"
#                             "(4) STATUS MACHINE \n"
#                             "(5) TUBE STATUS \n"
#                             "(6) Enabke insert coins \n"
#                             "(R)eturn ").lower()
#             if s_r == '1':
#                 cW.enableInsertCoins()
#                 cW.startReceivingMode()
#                 break
#             elif s_r == '2':
#                 qnty = ' '
#                 while qnty in (' '):
#                     qnty = input("Quantity to pay")
#                 print(cW.cashBackRoutine(float(qnty)))
#                 break
#             elif s_r == '3':
#                 print("Reset")
#                 cW.reset()
#                 break
#             elif s_r == '4':
#                 print("setup")
#                 cW.setup()
#                 break
#             elif s_r == '5':
#                 cW.tubeStatus()
#                 break
#             elif s_r == '6':
#                cW.enableInsertCoins()
#                break

