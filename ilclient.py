import time, sys, Queue, socket, ilcommand
from multiprocessing import Process
from multiprocessing.managers import BaseManager

'''
message_base = 1024
message_connect = ilcommand.message_base * 1
message_keep_alive = ilcommand.message_base * 2
message_command = ilcommand.message_base * 3
message_info = ilcommand.message_base * 4
message_disconnect = ilcommand.message_base * 5
'''

ip = socket.gethostbyname(socket.gethostname())
port = 2048
target = 'target.zip'
config = 'config.zip'

class QueueClient(BaseManager):
    pass

QueueClient.register('get_task_queue')
QueueClient.register('get_result_queue')

class ilworker(object):
    def __init__(self, server, port, key):
        self.manager = QueueClient(address=(server, port), authkey=key)
        
    def run(self):
        self.manager.connect()
        print('[+]\tconnected server')
        self.task = self.manager.get_task_queue()
        self.result = self.manager.get_result_queue()
        self.handle_message()
        
    def handle_message(self):
        #send connected message
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
                addr = {}
                addr['ip'] = ip
                addr['port'] = port
                addr['key'] = 'illa'
                self.task.put(ilcommand.message_command)
                self.task.put('client address')
                self.task.put(addr)
                print('[*]\ttell server my address = (%s)' % addr)
            elif r == ilcommand.message_command :
                pass
            elif r == ilcommand.message_info:
                r = self.result.get(timeout = 100)
                print '[*]\t' + r
            elif r == ilcommand.message_disconnect :
                print('[+]\tdisconnected to server')
                break
            
    def stop(self):
        pass
    
'''server task'''
class QueueServer(BaseManager):
    pass

global_task_queue = Queue.Queue()
global_result_queue = Queue.Queue()

QueueServer.register('get_task_queue', callable=lambda: global_task_queue)
QueueServer.register('get_result_queue', callable=lambda: global_result_queue)

class ilservertask(object):
    def __init__(self, port, key):
        self.manager = QueueServer(address=('', port), authkey = key)     
        
    def run(self):
        self.manager.start()   
        print('[+]\tstart server task')
        self.task = self.manager.get_task_queue()
        self.result = self.manager.get_result_queue()
        self.handle_message()
        
    def stop(self):
        self.manager.shutdown()
        
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
                print('[+]\tclient connected to server task')
                self.result.put(ilcommand.message_connect)
                
                self.result.put(ilcommand.message_command)
                self.result.put('pack')
                t = {}  
                t['target'] = target
                t['config'] = config
                self.result.put(t)
                
            elif r == ilcommand.message_command:
                self.handle_elfpack_message()
            elif r == ilcommand.message_info:
                r = self.task.get(timeout = 100)
                print '[*]\t' + r
            elif r == ilcommand.message_disconnect:
                break
            else:
                self.result.put(ilcommand.message_keep_alive)
                
    def handle_elfpack_message(self):
        r = self.task.get(timeout = 100)
        if r == 'packed':
            t = self.task.get(timeout = 100)
            #cleate proc handle it
            print('[*]\tpacked out path = %s' % t['path'])
            #close client
            self.result.put(ilcommand.message_disconnect)           
        
                
def server_task(p, k):
    s = ilservertask(p, k)
    s.run()
    s.stop()

if __name__ == '__main__':
    #w = ilworker('172.16.210.141', 5004, 'illa')
    w = ilworker(sys.argv[1], int(sys.argv[2]), sys.argv[3])
    print('[+]\tconnect to server address(%s:%s) server key(%s)' % (sys.argv[1], sys.argv[2], sys.argv[3]))
    if len(sys.argv) > 4:
        target = sys.argv[4]
        config = sys.argv[5]
    try:
        p = Process(target=server_task, args=(port,'illa'))
        p.start()
        w.run()
        p.join()
        
    except BaseException, e:
        print e
    finally:
        w.stop()
    