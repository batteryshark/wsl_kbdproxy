import platform
import os
import socket
from threading import Thread
import atexit
SOMAXCONN = 0x7fffffff

IS_WINDOWS = False
if platform.system() == "Windows":
    import ws2_32
    ws2_32.WSAStart()
    IS_WINDOWS = True


class AFUnixServer:
    def __init__(self, path,mode,request_procesor,request_add_args=[],buffer_size=0x1000):
        self.server = None
        self.request_add_args = request_add_args
        self.path = path
        if os.path.exists(path):
            os.unlink(path) 

        atexit.register(self.shutdown)
        self.request_processor = request_procesor
        self.buffer_size = buffer_size
        self.is_running = False
        if mode == "recv":
            self.comm_thread = Thread(target=self.recv_loop)
        elif mode == "send":
            self.comm_thread = Thread(target=self.send_loop)
        elif mode == "recvsend":
            self.comm_thread = Thread(target=self.recvsend_loop)
            
        self.comm_thread.setDaemon(True)

    def startup(self): 
        
        self.comm_thread.start()

    def setup_socket(self):
        if IS_WINDOWS:
            self.server = ws2_32.create_socket(ws2_32.AF_UNIX, ws2_32.SOCK_STREAM)
            ws2_32.bind_socket_un(self.server,ws2_32.AF_UNIX,self.path)
            ws2_32.listen_socket(self.server)
        else:
            self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.server.bind(self.path)     
            self.server.listen(SOMAXCONN)

        if not self.server:
            print(f"[AFUNIX] Unable to Bind Server Endpoint")
            return False
        return True

    def recv_loop(self):
        if not self.setup_socket():
            return
        self.is_running = True

        while self.is_running:
            if IS_WINDOWS:
                client = ws2_32.accept_connection(self.server)
                if not client:
                    continue
                data = ws2_32.recv_socket(client,self.buffer_size)
                ws2_32.shutdown_socket(client)
                if data:
                    args = [data.decode('utf-8',errors="replace")]
                    args.extend(self.request_add_args)                    
                    self.request_processor(args)
            else:
                client, addr = self.server.accept()
                data = client.recv(self.buffer_size)
                if data:
                    args = [data.decode('utf-8',errors="replace")]
                    args.extend(self.request_add_args)
                    self.request_processor(args)
                client.close()
            
    def send_loop(self):        
        return None
                

    def recvsend_loop(self):
        if not self.setup_socket():
            print("Setup Socket Failed")
            return
        self.is_running = True

        while self.is_running:
            if IS_WINDOWS:
                client = ws2_32.accept_connection(self.server)
                if not client:
                    continue
                data = ws2_32.recv_socket(client,self.buffer_size)
                if data:
                    args = [data.decode('utf-8',errors="replace")]
                    args.extend(self.request_add_args)                                      
                    response = self.request_processor(args)                    
                    ws2_32.send_socket(client,response)
                ws2_32.shutdown_socket(client)                    
            else:
                client, addr = self.server.accept()
                data = client.recv(self.buffer_size)
                if data:
                    args = [data.decode('utf-8',errors="replace")]
                    args.extend(self.request_add_args)                                      
                    response = self.request_processor(args)
                    client.send(response)
                client.close()

    def shutdown(self):
        self.is_running = False
        if self.server:
            if IS_WINDOWS:
                ws2_32.close_socket(self.server)
            else:
                self.server.close()


        if os.path.exists(self.path):
            os.unlink(self.path)

    def __del__(self):
        self.shutdown()

def print_string(msg):
    print(msg)

if __name__ == "__main__":
    rsvr = AFUnixServer("/tmp/LOGGER","recv",print_string)
    rsvr.startup()
    wat = input(" Press Any Key to Stop \n")
    rsvr.shutdown()
