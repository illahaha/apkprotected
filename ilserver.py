import time, sys, Queue, os, iltask, ilcommand
from multiprocessing.managers import BaseManager
from multiprocessing import Process

'''
message_base = 1024
message_connect = ilcommand.message_base * 1
message_keep_alive = ilcommand.message_base * 2
message_command = ilcommand.message_base * 3
message_info = ilcommand.message_base * 4
message_disconnect = ilcommand.message_base * 5
'''

taskdir = 'task'

class QueueServer(BaseManager):
    pass

global_task_queue = Queue.Queue()
global_result_queue = Queue.Queue()

QueueServer.register('get_task_queue', callable=lambda: global_task_queue)
QueueServer.register('get_result_queue', callable=lambda: global_result_queue)

class ilserver(object):
    def __init__(self, port, key):
        self.manager = QueueServer(address=('', port), authkey = key)     
        
    def run(self):
        self.manager.start()   
        print('[+]\tstart server')
        self.task = self.manager.get_task_queue()
        self.result = self.manager.get_result_queue()
        self.handle_message()
        
    def handle_message(self):
        while(True):
            try:
                r = self.task.get(timeout = 100)
            except BaseException, e:
                print e
                continue
            finally:
                pass
            
            if r == ilcommand.message_connect:
                print('\t=================================================================')
                print('\t')
                print('\t=================================================================')
                print('[+]\tclient connected')
                self.result.put(ilcommand.message_connect)
            elif r == ilcommand.message_command:
                r = self.task.get(timeout = 100)
                if r == 'client address':
                    addr = self.task.get(timeout = 100)
                    #cleate proc handle it
                    print('[*]\thandle client %s task' % addr)
                    p = Process(target=client_task, args=(addr['ip'], addr['port'], addr['key']))
                    p.start()
                    #close client
                    self.result.put(ilcommand.message_disconnect)
            elif r == ilcommand.message_info:
                r = self.task.get(timeout = 100)
                print '[+]\t' + r
            elif r == ilcommand.message_disconnect:
                pass
            else:
                self.result.put(ilcommand.message_keep_alive)   
        
    def stop():
        self.manager.shutdown()
        
        
'''client task'''
class QueueClient(BaseManager):
    pass

QueueClient.register('get_task_queue')
QueueClient.register('get_result_queue') 

class ilclientask(object):
    def __init__(self, server, port, key):
        self.manager = QueueClient(address=(server, port), authkey=key)

    def run(self):
        self.manager.connect()
        print('[+]\tconnected client handle')
        self.task = self.manager.get_task_queue()
        self.result = self.manager.get_result_queue()
        self.handle_message()
        
    def stop(self):
        pass#self.manager.shutdown()    
            
    def handle_message(self):
        self.task.put(ilcommand.message_connect)
        while True:
            try:
                r = self.result.get(timeout = 100)
            except BaseException, e:
                print e
                continue
            finally:
                pass
                    
            if r == ilcommand.message_keep_alive :
                continue
            elif r == ilcommand.message_connect:
                print('[+]\tconnected to client task')
            elif r == ilcommand.message_command :
                iltask.handle_elfpack_message(self.result, self.task, taskdir)
            elif r == ilcommand.message_info:
                r = self.result.get(timeout = 100)
                print '[+]\t' + r
            elif r == ilcommand.message_disconnect :
                print('[+]\tclient disconnected')
                print('\t=================================================================')
                print('\t')
                print('\t=================================================================')
                print(' ')
                print(' ')
                #close client task
                self.task.put(ilcommand.message_disconnect)                
                break        
         
'''
    def handle_elfpack_message(self):
        r = self.result.get(timeout = 100)
        if r == 'pack':
            r = self.result.get(timeout = 100)
            print('[*]\thandle client task')
            taskdir = os.path.join('task', str(os.getpid()))
            task = iltask(taskdir, 'leve', 'toolchain', r['target'], r['config'])
            task.handle()
            task.finished()
            
            #packed
            self.task.put(ilcommand.message_command)
            self.task.put('packed')
            t = {}
            t['path'] = os.path.join(os.path.join(taskdir, 'target'), 'target.zip')
            self.task.put(t)
            print('[+]\thandle finished and output = %s' % t)  
            
            #finished
            self.task.put(ilcommand.message_info)
            self.task.put('pack finished')
'''
        
def client_task(ip, port, key):
    c = ilclientask(ip, port, key)
    c.run()
    c.stop()
    
    
if __name__ == '__main__':
    #m = ilserver(5004, 'illa')
    print('[+]\tserver port (%s) server key(%s)' % (sys.argv[1], sys.argv[2]))
    m = ilserver(int(sys.argv[1]), sys.argv[2])
    if len(sys.argv) > 3:
        taskdir = sys.argv[3]
    try:
        m.run()
    except BaseException, e:
        print e
    finally:
        m.stop
        