"""
connor-compliant fifo wrapper
"""

import os
import struct
import errno
from enum import Enum


BIFO_BUFFER_SIZE: int = 2048


class StrBIFOSide(Enum):
    SERVER = 0x00,
    CLIENT = 0x01


def _create_if_not_exist(filename: str):
    try:
        os.mkfifo(filename)
    except OSError as oe: 
        if oe.errno != errno.EEXIST:
            raise

class StrBIFO:
    def __init__(self, side: StrBIFOSide, name: str, path="/tmp"):
        server_filename: str = f'{path}/{name}.server'
        client_filename: str = f'{path}/{name}.client'

        if side == StrBIFOSide.SERVER:
            self.__send_filename = server_filename
            self.__recv_filename = client_filename
        else:
            self.__send_filename = client_filename
            self.__recv_filename = server_filename

        _create_if_not_exist(self.__send_filename)
        _create_if_not_exist(self.__recv_filename)

        self.__send_fd = os.open(self.__send_filename, os.O_RDWR)
        self.__recv_fd = os.open(self.__recv_filename, os.O_RDWR)

    def close(self):
        os.close(self.__send_fd)
        os.close(self.__recv_fd)
    
    def read(self) -> str:
        binary_length = os.read(self.__recv_fd, struct.calcsize('@N'))
        length = struct.unpack('@N', binary_length)[0]
        return os.read(self.__recv_fd, length).decode('utf-8')
    
    def write(self, msg: str):
        data = bytes(msg, 'utf-8')
        length = struct.pack('@N', len(data))
        os.write(self.__send_fd, length)
        os.write(self.__send_fd, data)
        #os.write(self.__send_fd, bytes(msg, 'utf-8'))


if __name__ == '__main__':
    bifo = StrBIFO(StrBIFOSide.CLIENT, 'deutschlehrer')
    bifo.write("add_word")
    bifo.write("Testungswortgebilde")
    print(bifo.read())
    #print(bifo.read())
    bifo.write("exit")
