import os
import shutil
import zipfile

__author__ = 'illa'
__version__ = 'version 0.1'

class ilzip(object):
    def __init__(self, i, o):
        self._in = i
        self._out = o
    def pack(self):
        try:
            if os.path.exists(self._out):
                os.remove(self._out)
            z = zipfile.ZipFile(self._out, 'w', zipfile.ZIP_DEFLATED)
            n = len(self._in) + 1
            for base, dirs, files in os.walk(self._in):
                for file in files:
                    f = os.path.join(base, file)
                    z.write(f, f[n:])
        except StandardError, e:
            print e
        finally:
            z.close()
            
    def unpack(self):
        try:
            top = self._out
            if os.path.exists(self._out):
                shutil.rmtree(self._out)
            os.mkdir(self._out)
            z = zipfile.ZipFile(self._in)
            for n in z.namelist():
                (d,f) = os.path.split(n)
                z.extract(n, top)
        except StandardError, e:
            print e
        finally:
            z.close()
            
if __name__ == '__main__':
    z = ilzip('a.zip', 'a')
    z.unpack()
    z = ilzip('a', 'a.zip')
    z.pack()