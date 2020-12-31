import os
import socket
import struct
import sys
import time
from threading import Thread
import getch
import signal
from scapy.arch import get_if_addr

os.system("")

UDP_PORT = 13117
MESSAGE_LENGTH = 1024
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


# Handle signal to escape blocking thread
def handler(signum, frame):
    raise Exception()


"""
method: get_from_server
purpose: get messages from the server
"""


def get_from_server(sock):
    while True:  # prints messages from server
        time.sleep(0.1)
        try:
            sys.stdout.write(style.GREEN + sock.recv(MESSAGE_LENGTH).decode())
        except:
            break


print(style.YELLOW + "Client started, listening for offer requests...")  # waits for server suggestion
while True:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # init UDP socket
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((BROADCAST_IP, UDP_PORT))
    data, address = sock.recvfrom(MESSAGE_LENGTH)
    server_ip_address = str(address[0])
    try:
        cookie, message_type, server_tcp_port = struct.unpack('LBH', data)  # get message in specific format
        if cookie == 0xfeedbeef or message_type == 0x2:  # check if message is as expected
            print("Received offer from " + server_ip_address + " attempting to connect...")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # init TCP socket
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.connect((server_ip_address, server_tcp_port))
            name = input("Type In Your Nickname: ")
            sock.sendall(name.encode())  # send team's name to server
            sys.stdout.write(style.GREEN + sock.recv(MESSAGE_LENGTH).decode())  # the game begin message
            printer = Thread(target=get_from_server, args=(sock,))
            printer.start()
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(TIME_TO_PLAY)
            while True:
                try:
                    ch = getch.getch().encode()  # blocking, wait for char
                    sock.sendall(ch)  # if socket is still open, send it
                except:
                    break
        else:
            print("Bad UDP Message Format")  # got message not in the expected format
    except Exception as e:
        pass
