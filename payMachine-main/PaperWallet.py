# -*- coding: utf-8 -*-
"""
 @Author: Daniel Burruchaga Sola
        @Date: 25-04-22

Example:


Todo:
    * Review some doc
    * Review Feature auto-select port

|--------PaperWallet------|
|        __init__     setup()
|                     reset()
|                     tubeStatus()
|                     poll()
|                     coinType()
|                     dispense()
|                     enableInsertCoins()
|                         |
|-------------------------|

Ejemplo de uso:

pW = coinWallet()
pW.setup()
pW.reset()

"""

import BuchuSerial


class PaperWallet():
    # initialize the  connection to the com port
    def __init__(self):
        self.conn = BuchuSerial.BuchuSerial()

    def reset(self):  # [0xFC,0x05,0x40,0x2B,0x15]
        command = bytes(0x40)
        response = self.conn.serialSend(command)
        print(response)
        return response
    def requestStatus(self):
        command = bytearray([0xFC, 0x05, 0x11, 0x27, 0x56])
        response = self.conn.serialSend(command)
        print(response)
        return response

    """ HelpFull function for convert payload"""
    def __reciclerConvert(boxConfig, nBox):
        bytesConfBox = bytearray([0x00, 0x00, 0x00])
        if(boxConfig == 0):
            bytesConfBox[0] = 0x00
        if(boxConfig == 5):
            bytesConfBox[0] = 0x02
        if(boxConfig == 10):
            bytesConfBox[0] = 0x04
        if(boxConfig == 20):
            bytesConfBox[0] = 0x08
        if(boxConfig == 50):
            bytesConfBox[0] = 0x10
        if(boxConfig == 100):
            bytesConfBox[0] = 0x20

        if(nBox == 1):
            bytesConfBox[3] = 0x01
        if(nBox == 2):
            bytesConfBox[3] = 0x02

        return bytesConfBox

    """ Configura de donde se van a utilizar los billetes
    6 data bytes en hex ==>   xx   00   01      xx   00   02
                            config     box1   config     box2
    xx= 00 no se recicla
    xx = 02 se reciclan de 5€
    xx = 04 se reciclan de 10€
    xx = 08 se reciclan de 20€
    xx = 10 se reciclan de 50€
    xx = 20  NO se reciclan de 100€
    """

    def reciclerConfig(self, box1Config, box2Config):  # 0x02 0x00 0x01 0x04 0x00 0x02
        headerCommand = bytearray([0xFC, 0x0D, 0xF0, 0x20, 0xD0])
        byteConfBox1 = self.__reciclerConvert(box1Config, 1)
        byteConfBox2 = self.__reciclerConvert(box2Config, 2)
        finalCommand = bytearray([0x19, 0xE7])

        command = headerCommand + byteConfBox1 + byteConfBox2 + finalCommand

        response = self.conn.serialSend(command)
        print(response)
        return response

    """
        Configura con mode = 0 =>  para aceptar pagos el billetero
        Configura con mdoe = 1 => para realizar un pago mediante el billetero (devolucion de billetes)
    """
    def setModeInhibit(self, mode):  

        headerCommand = bytearray([0xFC, 0x06, 0xC3])
        if(mode == 0):
            dataCommand = bytearray([0x00])
        if(mode == 1):
            dataCommand = bytearray([0x01])
        finalCommand = bytearray([0x04, 0xD6])

        command = headerCommand + dataCommand + finalCommand

        response = self.conn.serialSend(command)
        print(response)
        return response

    """
    El pago mediante billetero se ha de realizar seleccionando el numero de 
    billetes a devolver y el numero de box de la que obtener el billete  
    mediante numBills seleccionamos el numero de billetes
    y con box seleccionamos el numero de box de la que obtener el billete
    """
    def payout(self,numBills, box):  
        headerCommand = bytearray([0xFC, 0x09, 0xF0])
        dataCommand = bytearray([0x20,0x4A,hex(numBills),hex(box)])
        finalCommand = bytearray([0x21, 0x63])

        command = headerCommand + dataCommand + finalCommand

        response = self.conn.serialSend(command)
        print(response)
        return response

    def getReady(self):
        #reset
        self.reset()
        #configurar para billetes de 5 box1 y billetes de 10 box2
        self.reciclerConfig(5,10)
        #Aceptar Pagos
        self.setModeInhibit



pW = PaperWallet()
pW.reset()
