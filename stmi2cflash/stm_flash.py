import sys
import os
import time
import array as arr
from smbus2 import SMBus, i2c_msg
from stm_i2c import *

def stm_write_data(data):
    with SMBus(1) as bus:
       msg = i2c_msg.write(0x38, data)
       bus.i2c_rdwr(msg)

def stm_read_data(data):
    with SMBus(1) as bus:
       msg = i2c_msg.read(0x38, data)
       bus.i2c_rdwr(msg)
       return list(msg)

def stm_flash(buf):
    print 'stm32 i2c programming'
    stm = stm_i2c(stm_read_data, stm_write_data)
    stm.stm_getversion()
    stm.stm_erase()
    stm.stm_program(buf)

def file_read(file):
    buffer = []
    file = os.path.normcase(os.path.normpath(file))
    if not os.path.isfile(file):
        print "Input file not found!"
        sys.exit(1)
    else:
        file = open(file, "rb")
        buffer = file.read()
        file.close()
    return buffer    

if __name__ == '__main__':
    stm_buf = arr.array('B', file_read(sys.argv[1]))
    stm_flash(stm_buf)
