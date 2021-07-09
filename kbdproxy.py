import ctypes
import time
import struct

#from pyafunix import AFUnixServer
import socket

u32 = ctypes.CDLL("user32.dll")

GetAsyncKeyState = u32.GetAsyncKeyState
GetAsyncKeyState.restype = ctypes.c_uint16
GetAsyncKeyState.argtypes = [ctypes.c_int]

VK_Z = 0x5A
VK_C = 0x43
VK_S = 0x53
VK_Q = 0x51
VK_E = 0x45

VK_F1 = 0x70
VK_F2 = 0x71
VK_F3 = 0x72
VK_F4 = 0x73
VK_F12 = 0x7B
VK_1 = 0x31
VK_5 = 0x35


KEY_DB = {
VK_Z:{'val':0,'unix':44},
VK_C:{'val':0,'unix':46},
VK_S:{'val':0,'unix':31},
VK_Q:{'val':0,'unix':16},
VK_E:{'val':0,'unix':18},
VK_F1:{'val':0,'unix':59},
VK_F2:{'val':0,'unix':60},
VK_F3:{'val':0,'unix':61},
VK_F4:{'val':0,'unix':62},
VK_F12:{'val':0,'unix':88},
VK_1:{'val':0,'unix':2},
VK_5:{'val':0,'unix':6}
}
"""
struct input_event {
    struct timeval time;
    __u16 type;
    __u16 code;
    __s32 value;
};
"""

EV_KEY = b"\x01\x00"
VAL_UP = b"\x00\x00\x00\x00"
VAL_DOWN = b"\x01\x00\x00\x00"
def create_input_event(d):
    outdata = b"\x00\x00\x00\x00\x00\x00\x00\x00"
    outdata += EV_KEY
    outdata += struct.pack("<H",d['unix'])
    if d['val']:
        print("VAL DOWN")
        outdata += VAL_DOWN
    else:
        print("VAL UP")
        outdata += VAL_UP
        
    return outdata

def update_input(sock):
    evdata = b""
    for item in KEY_DB:
        nval = GetAsyncKeyState(item) & 0x8000
        if nval != KEY_DB[item]['val']:
            KEY_DB[item]['val'] = nval
            evdata += create_input_event(KEY_DB[item])
    if len(evdata):
        print("Send_DATA")        
        sock.send(evdata)





def setup_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("127.0.0.1", 12341))
    return sock




    # Terminate
    sock.close(  )

if __name__ == "__main__":
    #aus = AFUnixServer("d:\\wsl\\server.sock","recvsend",update_input)
    #aus.startup()
    sock = setup_server()
    while 1:
        update_input(sock)
    wat = input("Press any key to stop")
        # Write data out
#if ((GetAsyncKeyState(IOBindings.p1_start) & 0x8000)) { value |= 1u; }      // P1 Start
#time EV_KEY code 44 (KEY_Z) value 0 (up) / down is 1