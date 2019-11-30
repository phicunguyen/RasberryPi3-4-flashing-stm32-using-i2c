import sys
import array
import os
import time
import array as arr
from smbus2 import SMBus, i2c_msg

BURST_WRITE_SIZE                            = 256
STM_STAT_ACK                                = 0x79
STM_STAT_NACK                               = 0x1F
STM_STAT_BUSY                               = 0x76
STM_GET_VERSION                             = 0x01
STM_NO_STRETCH_WRITE_MEMORY                 = 0x32
STM_ERASE_COMMAND                           = 0x44

class stm_i2c(object):
    
    def __init__(self, read, write):
	self.read = read
	self.write = write
	
    def stm_write(self, data):
	self.write(data)

    def stm_read(self, len):
	return self.read(len)

    def stm_getversion(self):
        if not self.stm_command_set(STM_GET_VERSION):   
            ver = self.stm_read(0x1)
            if not self.stm_wait_for_ack():   
                print "Version: ", hex(ver[0])
                return
            else:
                print "Could not get version"
        else:
            print "failed to get ACK"
           
    def stm_wait_for_ack(self):
        error = 0
        count = 20
        while count:
            ack = self.stm_read(1)
            if ack[0] is not None:
                if ack[0] == STM_STAT_ACK:
                    break
                elif ack[0] == STM_STAT_BUSY:
                    continue
                else:
                    error = 1
                    break
            else:
                error = 2
                break
            count -= 1
        return error

    def stm_command_set(self, cmd):
        self.stm_write(arr.array('B', [cmd, cmd ^ 0xFF])) 
        return self.stm_wait_for_ack()

    def stm_address_set(self, addr):
        addr = arr.array('B', [(addr>>24)&0xFF, (addr>>16)&0xFF, (addr>>8)&0xFF, addr&0xff])
        addr.append(addr[0] ^ addr[1] ^ addr[2] ^ addr[3])
        self.stm_write(addr) # Send address
        return self.stm_wait_for_ack()

    def stm_length_set(self, len):
        len -= 1
        # Send burst size
        self.stm_write(arr.array('B', [len, len ^ 0xFF])) 
        
    def stm_page_write(self, addr, data):
        error = 0
        size  = len(data)
        page  = arr.array('B', [])
        al    = (size + 3) & ~3;
        cs    = al - 1
        error = self.stm_command_set(STM_NO_STRETCH_WRITE_MEMORY) 
        if not error:
            error = self.stm_address_set(0x8000000 + addr) 
        if not error:
            page.append(cs)
            for i in range(size):
                tmp = data[i]
                cs ^= tmp;
                page.append(tmp)
            page.append(cs)
            error = self.stm_write(page) 
        if not error:
            error = self.stm_wait_for_ack()
        return error

    def stm_erase(self):
        self.print_message("Erasing...")
        error = self.stm_command_set(STM_ERASE_COMMAND) 
        if not error:
            error = self.stm_write(arr.array('B', [0xFF, 0xFF, 0x00])) 
        if not error:
            # wait 40 seconds to ensure flash is erased
            self.sleep(40.0) 
            self.progress_indicator_close("done")
            
    def stm_program(self, data):
        addr  = 0
        size  = len(data)
        error = 0
        addr  = 0
        self.print_message("Programming...")
        self.progress_indicator_open(size)        
        while True:
            burst_len = len(data)
            if burst_len >= BURST_WRITE_SIZE:
                burst_len = BURST_WRITE_SIZE
            if burst_len:
                error = self.stm_page_write(addr, data[:burst_len])
            if error or not burst_len:
                break
            addr     += burst_len
            data = data[burst_len:] # remove sent data from data
            self.progress_indicator_update(addr)
        if error:
            self.progress_indicator_close("failed")
        else:
            self.progress_indicator_close("done") 

    def progress_indicator_open(self, total):
        self.ind_tot = total
        self.ind_str = ""
        self.progress_indicator_update(0)

    def progress_indicator_close(self, str):
        bs_str  = '\b'*len(self.ind_str)
        self.ind_str = ""
        sys.stdout.write(bs_str + str + '\n')
        sys.stdout.flush()

    def sleep(self, time_tot):
        time_inc = 0.0
        self.progress_indicator_open(time_tot)
        while True:
            time.sleep(0.5)
            time_inc += 0.5
            self.progress_indicator_update(time_inc)
            if time_inc > time_tot:
                break

    def progress_indicator_update(self, completed):
        p = (float(completed) / self.ind_tot) * 100
        if p > 100.0:
            p = 100.0
        bs_str  = '\b'*len(self.ind_str)
        new_str = "%d%%" % int(p)
        if new_str != self.ind_str:
            self.ind_str = new_str
            sys.stdout.write(bs_str + self.ind_str)
            sys.stdout.flush()
                
    def print_message(self, str):
        sys.stdout.write(str)
        sys.stdout.flush()
