import serial
def Serial():
    def begin(baud,port):
        try:
            print("Connecting...")
            portConfig  = serial.Serial(port = port,
                            baudrate = baud,
                            bytesize = serial.EIGHTBITS,
                            parity   = serial.PARITY_NONE,
                            stopbits = serial.STOPBITS_ONE)
        except:
            SerialBegin(baud)
            print("Reconnecting TTGO")
            time.sleep(5)
            pass
        return portConfig
    def serialWrite(portConfig,xData):
        portConfig.write(str(xData).encode())

    def serialClose(portConfig):
        portConfig.close()

    def serialOpen(portConfig):
        portConfig.open()

    def serialRead(portConfig):
        return portConfig.readline()

    def serialAvailable(portConfig):
        if(portConfig.in_waiting):
            return True
        else:
            return False