# -*- coding: utf-8 -*-
"""
 @Author: Daniel Burruchaga Sola
        @Date: 25-04-22

Example:


Todo:
    * Review some doc
    * Review Feature auto-select port

|--------PaperWallet------|
|        __init__     reset()
|                     powerOn()
|                     poll()
|                     payout()
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
        



pW = PaperWallet()
pW.getReady()
