import time

import serial


class Center309:
    def __init__(self, comport, baudrate, stopbits):
        self.serialport = serial.Serial()
        self.serialport.port = comport
        self.serialport.baudrate = baudrate
        self.serialport.stopbits = stopbits

    def __del__(self):
        self.serialport.close()

    def read_temperature(self, channel_number):
        if not self.serialport.isOpen():
            self.serialport.open()
        self.serialport.write(b'A')
        resp = self.serialport.read(45)
        first_channels_byte = 7
        bytes_toread_indexes = [first_channels_byte + 2 * (channel_number - 1),
                                first_channels_byte + 2 * (channel_number - 1) + 1]
        bytehigh_value = resp[bytes_toread_indexes[0]]
        bytelow_value = resp[bytes_toread_indexes[1]]
        temperature = int.from_bytes([bytehigh_value, bytelow_value], "big") / 10
        return temperature

    # def identify(self):
    #     if not self.serialport.isOpen():
    #         self.serialport.open()
    #     self.serialport.write(b'K')
    #     time.sleep(1)
    #     resp = self.serialport.read(100)
    #     return resp
