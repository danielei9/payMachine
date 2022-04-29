# -*- coding: utf-8 -*-
"""
 @Author: Daniel Burruchaga Sola
        @Date: 25-04-22

Example:
    portConfig = s.serialBegin(baudrate)  open the port

Todo:
    * Review some doc and 
    * Feature auto-select port

"""
import serial
import glob
import time


class BuchuSerial():
    baudrate = 9600
    
    def __init__(self):
        portConfig = self.serialBegin(self.baudrate)

# Setter  for serial baudrete
    def setBaudrate(self, _baudrate):
        self.baudrate = _baudrate

# Can check all available ports and select one 
# TODO: check auto-selection
    def serial_ports(self):
        ports = glob.glob('/dev/tty[A-Za-z]*')
        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        print(result)
        return result

# Begin serial connection
    def serialBegin(self, baud):
        try:
            ports = self.serial_ports()
            print("Connecting to " + str(ports))
            portConfig = serial.Serial(port=ports[0],
                                       baudrate=baud,
                                       bytesize=serial.EIGHTBITS,
                                       parity=serial.PARITY_NONE,
                                       stopbits=serial.STOPBITS_ONE)
        except:
            print("ReConnecting to " + str(self.serial_ports()[0]))
            time.sleep(5)
            self.serialBegin(baud)
            return False
            # pass
        return portConfig

# Write a string with serial 
    def serialWriteString(self, xData):
        try:
            self.portConfig.write(str(xData).encode())
            return True
        except serial.SerialException:
            print('Port is not available')
            self.portConfig.close()
            print('tryin to reconnect port')
            time.sleep(2)
            self.serialBegin(9600)

        except serial.portNotOpenError:
            print('Attempting to use a port that is not open')
        except:
            self.portConfig.close()
            time.sleep(2)
            self.serialBegin(9600)
            return False

#Raw serial write
    def serialWrite(self, xData):
        try:
            self.portConfig.write(xData)
            return True
        except serial.SerialException:
            print('Port is not available')
            self.portConfig.close()
            print('tryin to reconnect port')
            time.sleep(2)
            self.serialBegin(9600)
        except serial.portNotOpenError:
            print('Attempting to use a port that is not open')
        except:
            self.portConfig.close()
            time.sleep(2)
            self.serialBegin(9600)
            return False

# Open a connection with the specified port 
    def serialOpen(self):
        try:
            self.portConfig.open()
            return True
        except serial.SerialException:
            print('Port is not available')
            return False
        except serial.portNotOpenError:
            print('Attempting to use a port that is not open')
            return False
        except:
            print("Not possible to open port")
            return False

# Read a line from serial
    def serialReadLine(self):
        try:
            return self.portConfig.readline()
        except serial.SerialException:
            print('Port is not available')
            return False
        except serial.portNotOpenError:
            print('Attempting to use a port that is not open')
            return False
        except:
            print("Not possible to read port")
            return False

# Read n bytes from serial port
    def serialxBytesToRead(self, n):
        try:
            return self.portConfig.read(n)
        except serial.SerialException:
            print('Port is not available')
            return False
        except serial.portNotOpenError:
            print('Attempting to use a port that is not open')
            return False
        except:
            print("Not possible to read port")
            return False

# If serial data is available then return true else false
    def serialAvailable(self):
        try:
            if(self.portConfig.in_waiting):
                return True
            else:
                return False
        except serial.SerialException:
            print('Port is not available')
            return False
        except serial.portNotOpenError:
            print('Attempting to use a port that is not open')
            return False

# Try to close if it is already open
    def serialClose(self):
        try:
            self.portConfig.close()
            return True
        except serial.SerialException:
            print('Port is not available')
        except serial.portNotOpenError:
            print('Attempting to use a port that is not open')
        except:
            print("Not possible to close port")
            return False

# Try ti send a command and return the answer from this command
    def serialSend(self, xData, TTL=2):
        # try to close if it is already open
        self.serialClose()
        # try to open
        self.serialOpen()
        # try to send
        self.serialWrite(xData)
        # try to read if available
        count = 0
        startTimeOut = time.time()
        while (not self.serialAvailable()):
            print("waiting response...")
            endTimeOut = time.time()
            time.sleep(1)
            # TimeOut
            if (endTimeOut - startTimeOut >= TTL):  # TODO: DEFINE TTL
                return -1
        response = self.serialReadLine()
        self.serialClose()
        return response
