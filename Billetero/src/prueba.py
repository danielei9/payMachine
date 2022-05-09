#!/usr/bin/env python
import serial
import time
import _thread as thread

UN_EURO = '08 54'
DOS_EURO = '08 55'
ZERO_ZERO_FIVE = '08 50'
ZERO_TEN = '08 51'
ZERO_TWNTY = '08 52'
ZERO_FIVETY = '08 53'


class MSerialPort:
    message=''
   
    def __init__(self,port,buand):
        self.bv_events = {
            DOS_EURO: self.__onInserted2Euro,
            UN_EURO: self.__onInsertedEuro,
            ZERO_FIVETY: self.__onInserted50Cent,
            ZERO_TWNTY: self.__onInserted20Cent,
            ZERO_TEN: self.__onInserted10Cent,
            ZERO_ZERO_FIVE: self.__onInserted05Cent,
        }
        self.port=serial.Serial(port,buand)
        if not self.port.isOpen():
            self.port.open()
            
    def port_open(self):
        if not self.port.isOpen():
            self.port.open()
            
    def port_close(self):
        self.port.close()
        
    def send_data(self,data):
        number = self.port.write(data)
        return number
    
    def read_data(self):
        while True:
            received=self.port.readline()
#             self.message=str(received)
            self.__parseBytes(received)
            print(self.status)
            print(self.data)

    def __parseBytes(self,received):
        status = str(received)[2:4]
        data = str(received)[5:(len(str(received))-5)]
        self.status = status.split(" ")
        self.data = data.split(" ")
#         print(type(self.status[0]))
        self.message = str(self.status[0] + " " + self.data[0])  
        if(self.message  in self.bv_events):
            self.bv_events[self.message ](data)
# # # # # # # # # # # # # # # # # # # # # # 
# EVENTS
# # # # # # # # # # # # # # # # # # # # # # 
   
    def __onInserted05Cent(self,data=''):
        if(self.data[0] == '50'  ):
            print("0.05 euro")
    def __onInserted10Cent(self,data=''):
        if(self.data[0] == '51'  ):
            print("0.10 euro")
    def __onInserted20Cent(self,data=''):
        if(self.data[0] == '52'  ):
            print("0.20 euro")
    def __onInserted50Cent(self,data=''):
        if(self.data[0] == '53'  ):
            print("0.50 euro")
    def __onInsertedEuro(self,data=''):
        if(self.data[0] == '54'):
            print("1 euro")
    def __onInserted2Euro(self,data=''):
        if(self.data[0] == '55'  ):
            print("2 euros")            
# # # # # # # # # # # # # # # # # # # # # # 
   
if __name__=='__main__':
    mSerial=MSerialPort('/dev/ttyUSB0',9600)
    thread.start_new_thread(mSerial.read_data,())
    while True:
        time.sleep(1)
        mSerial.message = ""