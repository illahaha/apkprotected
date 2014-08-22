import sys
import os
import struct

__author__ = 'illa'
__version__ = 'version 0.1'

EI_NIDENT = 16

class ilelf(object):
    def __init__(self, path):
        self.fname = path
        self.ehdr = {}
        try:
            f = open(self.fname, 'rb')
            self.e_ident = f.read(EI_NIDENT)
            tmp = f.read(struct.calcsize('2HI3QI6H'))
            tmp = struct.unpack('2HI3QI6H', tmp)
            self.e_type = tmp[0]
            self.e_machine = tmp[1]
            
            self.checkelf()
        except StandardError, e:
            print e
        finally:
            f.close()
            
    def checkelf(self):
        magic = [ord(i) for i in self.e_ident]
        if magic[0] != 127 or magic[1] != ord('E') or magic[2] != ord('L') or magic[3] != ord('F'):
            return False
        
        if magic[4] == 1:
            self.ehdr['arch'] = 'ELF32'
        elif magic[4] == 2:
            self.ehdr['arch'] = 'ELF64'
        else:
            self.ehdr['arch'] = 'UNKNOWN'
            
        if magic[5] == 1:
            self.ehdr['encoding'] = 'little-endian'
        elif magic[5] == 2:
            self.ehdr['encoding'] = 'big-endian'
        else:
            self.ehdr['encoding'] = 'UNKNOWN'
            
        if self.e_type == 0:
            self.ehdr['type'] = 'UNKNOWN'
        elif self.e_type == 1:
            self.ehdr['type'] = 'REL'
        elif self.e_type == 2:
            self.ehdr['type'] = 'EXEC'
        elif self.e_type == 3:
            self.ehdr['type'] = 'DYN'
        elif self.e_type == 4:
            self.ehdr['type'] = 'Core'
        else:
            self.ehdr['type'] = 'UNKNOWN'
            
        if self.e_machine == 40:
            self.ehdr['machine'] = 'ARM'
        elif self.e_machine == 3:
            #self.ehdr['machine'] = 'EM386'
            self.ehdr['machine'] = 'x86'
            
        return True
    
if __name__ == '__main__':
    elf = ilelf('gdbserver')
    elf.checkelf()
    print elf.ehdr['machine']
    
    elf = ilelf('libfishingjoy3.so')
    elf.checkelf()
    
    elf = ilelf('libsmsiap.so')
    elf.checkelf()
    
    
            
                                                                                             