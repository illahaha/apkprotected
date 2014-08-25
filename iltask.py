import sys, os, shutil, json, subprocess, commands, ilcommand
from ilzip import ilzip
from ilelf import ilelf

__author__ = 'illa'
__version__ = 'version 0.1'

class iltask(object):
    def __init__(self, taskdir, levedir, toolchain, target, config):
        self.var = {}
        self.var['dir'] = taskdir
        self.var['leve'] = levedir
        self.var['toolchain'] = toolchain
        self.var['targetdir'] = os.path.join(taskdir, 'target')
        self.var['configdir'] = os.path.join(taskdir,'config')
        self.var['logdir'] = os.path.join(taskdir, 'log')
        self.var['tmp'] = os.path.join(taskdir, 'tmp')
        self.var['target'] = target
        self.var['config'] = config
        
        try:
            if os.path.exists(self.var['dir']) :
                shutil.rmtree(self.var['dir'])
            os.mkdir(self.var['dir'])
            os.mkdir(self.var['targetdir'])
            os.mkdir(self.var['configdir'])
            os.mkdir(self.var['logdir'])   
            os.mkdir(self.var['tmp'])
            
            t = ilzip(self.var['target'], self.var['targetdir'])
            t.unpack()
            
            c = ilzip(self.var['config'], self.var['configdir'])
            c.unpack()
                
        except StandardError, e:
            print e
        finally:
            pass
        
    def handle(self):
        try:
            
            for base,dirs,files in os.walk(self.var['configdir']):
                for f in files:
                    fd = file(os.path.join(self.var['configdir'], f))
                    js = json.load(fd)
                    fd.close()
                    for k, v in js.items():
                        print '[+]\thandle target %s' % k
                        self.pack(k, js[k])
                        print '[+]\t------------------------------------'
        except StandardError, e:
            print e
        finally:
            pass
        
    def pack(self, key, value):
        isapk = False
        isdyn = False
        d = self.var['targetdir']
        f = key
        try:
            if key.split('.')[-1] == 'apk':
                isapk = True
                i = os.path.join(d, key)
                o = os.path.join(d, os.path.basename(key)[:-4])
                t = ilzip(i, o)
                t.unpack()
                d = os.path.join(d, os.path.basename(key)[:-4])
            elif key.split('.')[-1] == 'so':
                isdyn = True
                pass
            else:
                pass
    
            for v in value:
                self.pack1(d, v['path'], v['leve'])
                
            if isapk:
                z = ilzip(o, o + '.packed.apk')
                z.pack()
                os.remove(i)
                shutil.rmtree(d)
            if isdyn:
                o = os.path.join(d, v['path'])
                os.rename(o, os.path.join(d, v['path'][:-3] + '.packed.so'))
        except StandardError, e:
            print e
        finally:
            pass
        
    def pack1(self, d, t, l):
        try:
            target = os.path.join(d, t)
            targetlist = list()
            leve = os.path.join(self.var['leve'], l) + '.json'
            fd = file(leve)
            js = json.load(fd)
            fd.close()
            v = js['L1']
            for ldic in v:
                if os.path.isdir(target) == True:
                    isapk = True
                    for base, dirs, files in os.walk(target):
                        for f in files:
                            targetlist.append(os.path.join(base, f))
                else:
                    targetlist.append(target)
                    
            for item in targetlist:
                self.pack2(os.path.join(self.var['toolchain'],ldic['toolchain']), ldic['args'], item)
                
        except StandardError, e:
            print e
        finally:
            pass
        
    def pack2(self, toolchain, args, target):
        elf = ilelf(target)
        try:
            if elf.ehdr['type'] != 'DYN':
                return
            machine = elf.ehdr['machine']
            machine = machine.lower()
            args = args.replace('$DIR', self.var['toolchain'])
            args = args.replace('$MACHINE', machine)
            args = args.replace('$TARGET', target)
            self.pack3(toolchain, args, target)
        except BaseException, e:
            print e
        finally:
            pass
        
    def pack3(self, tool, args, target):
        try:
	    f = open(os.path.join(self.var['logdir'], 'log.txt'), mode='a')
	    f.write('========================' + '\n')
	    f.write(tool + ' ' + args + '\n')
            print '[*]\t', tool, args
      	    r,log = commands.getstatusoutput(tool+' '+args)
            f.write(log + '\n')
            r,log = commands.getstatusoutput('readelf -l'+' '+target)
            f.write(log + '\n')
            f.write('========================' + '\n\n')
            f.close()
        except BaseException, e:
            print e
        finally:
            pass
        
    def finished(self):
        i = self.var['targetdir']
        o = os.path.join(self.var['tmp'], 'target.zip')
        z = ilzip(i, o)
        z.pack()
        shutil.rmtree(i)
        os.mkdir(i)
        shutil.move(o, os.path.join(i, 'target.zip'))
        print '[+]\toutput path ====>>>> %s' % os.path.join(i, 'target.zip')
        
def handle_elfpack_message(result, task, workdir):
    r = result.get(timeout = 100)
    if r == 'pack':
        r = result.get(timeout = 100)
        print('[*]\thandle client task')
        taskdir = os.path.join(workdir, str(os.getpid()))
        elftask = iltask(taskdir, 'leve', 'toolchain', r['target'], r['config'])
        elftask.handle()
        elftask.finished()
        
        #packed
        task.put(ilcommand.message_command)
        task.put('packed')
        t = {}
        t['path'] = os.path.join(os.path.join(taskdir, 'target'), 'target.zip')
        task.put(t)
        print('[+]\thandle finished and output = %s' % t)  
        
        #finished
        task.put(ilcommand.message_info)
        task.put('pack finished')    
        
if __name__ == '__main__':
    t = task('task/3389', 'leve', 'toolchain', 'target.zip', 'config.zip')
    t.handle()
    t.finished()
    
