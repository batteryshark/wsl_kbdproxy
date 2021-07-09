from ctypes import *
from ctypes.wintypes import *


AF_UNIX = 1
SOCK_STREAM = 1
SOMAXCONN = 0x7FFFFFFF
SOCKET_ERROR = -1
INVALID_SOCKET = 0xFFFFFFFF

WSADESCRIPTION_LEN = 256
WSASYS_STATUS_LEN = 128
    
class WSADATA(ctypes.Structure):
    _fields_ = [
        ("wVersion",        WORD),
        ("wHighVersion",    WORD),
        ("szDescription",   c_char * (WSADESCRIPTION_LEN+1)),
        ("szSystemStatus",  c_char * (WSASYS_STATUS_LEN+1)),
        ("iMaxSockets",     c_ushort),
        ("iMaxUdpDg",       c_ushort),
        ("lpVendorInfo",    c_char_p),
    ]

class sockaddr_un(Structure):
    _fields_ = [("sa_family", c_ushort),  # sun_family
                ("sun_path", c_char * 1024)]

class sockaddr_in(Structure):
    _fields_ = [("sa_family", c_ushort),  # sin_family
                ("sin_port", c_ushort),
                ("sin_addr", c_byte * 4),
                ("__pad", c_byte * 8)]    # struct sockaddr_in is 16 bytes    
    
LP_WSADATA = POINTER(WSADATA)
    
WSAStartup = windll.Ws2_32.WSAStartup
WSAStartup.argtypes = (WORD, POINTER(WSADATA))
WSAStartup.restype = c_int

socket = windll.Ws2_32.socket
socket.argtypes = [c_int, c_int, c_int]
socket.restype = c_uint

bind = windll.Ws2_32.bind
bind.argtypes = [c_int, c_void_p, c_int]
bind.restype = c_int

connect = windll.Ws2_32.connect
connect.argtypes = [c_int, c_void_p, c_int]
connect.restype = c_int

closesocket = windll.Ws2_32.closesocket
closesocket.argtypes = [c_int]
closesocket.restype = c_int

listen = windll.Ws2_32.listen
listen.argtypes = [c_int,c_int]
listen.restype = c_int

accept = windll.Ws2_32.accept
accept.argtypes = [c_int,c_void_p,c_int]
accept.restype = c_int

recv = windll.Ws2_32.recv
recv.argtypes = [c_int,POINTER(c_ubyte),c_int,c_int]
recv.restype = c_int

send = windll.Ws2_32.send
send.argtypes = [c_int,c_void_p,c_int,c_int]
send.restype = c_int

shutdown = windll.Ws2_32.shutdown
shutdown.argtypes = [c_int,c_void_p,c_int]
shutdown.restype = c_int


DeleteFileA = windll.kernel32.DeleteFileA
DeleteFileA.argtypes = [c_char_p]
DeleteFileA.restype = BOOL

def SUN_LEN(path):
    """For AF_UNIX the addrlen is *not* sizeof(struct sockaddr_un)"""
    return ctypes.c_int(2 + len(path))

#bind(ListenSocket, (struct sockaddr*)&ServerSocket, sizeof(ServerSocket)

def WSAStart(): 
    def MAKEWORD(bLow, bHigh):
        return (bHigh << 8) + bLow
     
    wsaData = WSADATA()
    ret = WSAStartup(MAKEWORD(2, 2), LP_WSADATA(wsaData))
    if ret != 0:
        raise WinError(ret)
    return ret

def create_socket(socket_af, socket_type, socket_protocol=0):
    result = socket(socket_af, socket_type, socket_protocol)
    if result == INVALID_SOCKET:
        return None
    return result

def connect_socket_un(socket_fd, socket_af, path):
    path = path.encode('ascii')
    addr = sockaddr_un()
    addr.sa_family = socket_af
    addr.sun_path = path
    res = connect(socket_fd, byref(addr),SUN_LEN(path))
    if res == SOCKET_ERROR:
        return False
    return True

def bind_socket_un(socket_fd,socket_af,path):
    path = path.encode('ascii')
    addr = sockaddr_un()
    addr.sa_family = socket_af
    addr.sun_path = path
    res = bind(socket_fd, byref(addr),SUN_LEN(path))
    if res == SOCKET_ERROR:
        return False
    return True

def listen_socket(socket_fd,how=SOMAXCONN):
    res = listen(socket_fd,how)
    if res == SOCKET_ERROR:
        return False
    return True

def accept_connection(socket_fd):
    client_fd = accept(socket_fd,None,0)
    if client_fd == SOCKET_ERROR:
        return None
    return client_fd

def close_socket(socket_fd):
    return closesocket(socket_fd)

def shutdown_socket(socket_fd):
    return shutdown(socket_fd,None,0)

def recv_socket(socket_fd,amt):
    data = (c_ubyte * amt)()
    bytesread = recv(socket_fd,data,amt,0)
    if bytesread < 0:
        return b""
    return bytes(data[:bytesread])

def send_socket(socket_fd,data):
    byteswritten = send(socket_fd,data,len(data),0)
    if byteswritten == len(data):
        return True
    return False

def send_string(socket_fd,data):
    data = data.encode('ascii')
    return send_socket(socket_fd,data)

def recv_string(socket_fd,amt):
    data = recv_socket(socket_fd,amt)
    if len(data):
        return data.decode('utf-8',errors="replace")
    return ""

if __name__ == "__main__":
    WSAStart()
    sock_path = "C:\\tmp\\LOGGER"

    server = create_socket(AF_UNIX,SOCK_STREAM)
    print(server)
    res = bind_socket_un(server,AF_UNIX,sock_path)
    print("OK")

    res = listen_socket(server)
    print("OK 2")

    client_fd = accept_connection(server)
    if client_fd:
        data = recv_string(client_fd,4096)
        print(data)
        shutdown_socket(client_fd)

    close_socket(server)
    DeleteFileA(sock_path.encode('ascii'))
