import os
import socket
import struct
import sys
import time
from select import select
from threading import Thread
import getch
import signal

os.system("")

UDP_PORT = 13117
TCP_PORT = 5031
MESSAGE_LENGTH = 1024
CLIENT_NICKNAME = "RAK BIBI\n"
TIME_TO_PLAY = 10  # seconds
BROADCAST_IP = ""
sock = None
end = time.time()


# Group of Different functions for different styles
class style:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'


print(style.YELLOW + "Client started, listening for offer requests...")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((BROADCAST_IP, UDP_PORT))

def handler(signum, frame):
    raise Exception()

def print_messages(sock):
    while True:
        try:
            ch = getch.getch().encode() # blocking, wait for char
            sock.sendall(ch)    # if socket is still open, send it
        except:
            break   # if socket is closed, exit

def get_from_server(sock):
     while True:  # prints messages from server
              sys.stdout.write(style.GREEN + sock.recv(MESSAGE_LENGTH).decode())
   


 
while True:

    data, address = sock.recvfrom(MESSAGE_LENGTH)
    # server_ip_address = address[0]
    server_ip_address = "127.0.1.1"
    try:
        cookie, message_type, server_tcp_port = struct.unpack('LBH', data)
        if cookie == 0xfeedbeef or message_type == 0x2:
            print("Received offer from " + server_ip_address + " attempting to connect...")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.connect((server_ip_address, server_tcp_port))
            name = raw_input("Type In Your Nickname: ")
            sock.sendall(name.encode())

            reciever = Thread(target=print_messages, args=(sock,))
            sys.stdout.write(style.GREEN + sock.recv(MESSAGE_LENGTH).decode())  # the game begin message
            printer = Thread(target = get_from_server  , args =(sock,))
            printer.start()
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(TIME_TO_PLAY)
            while True:
                try:
                    ch = getch.getch().encode() # blocking, wait for char
                    sock.sendall(ch)    # if socket is still open, send it
                except:
                    break   # if socket is closed, exit
                    # send chars to server
                
            
            #while True:  # prints messages from server
             #   sys.stdout.write(style.GREEN + sock.recv(MESSAGE_LENGTH).decode())
        else:
            print("Bad UDP Message Format")
    except:
        pass
