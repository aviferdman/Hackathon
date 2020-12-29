import msvcrt
import os
import socket
import struct
import sys
import time

from pynput import keyboard

os.system("")

UDP_PORT = 13117
TCP_PORT = 5006
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


def pressed(pressed_key):
    if time.time() < end:
        try:
            ch = str(pressed_key)[1]  # '{0}', char
            sock.sendall(ch.encode())
        except:
            pass


while True:

    print(style.YELLOW + "Client started, listening for offer requests...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((BROADCAST_IP, UDP_PORT))
    data, address = sock.recvfrom(MESSAGE_LENGTH)
    server_ip_address = address[0]
    sock.close()
    cookie, message_type, server_tcp_port = struct.unpack('LBH', data)
    #   if cookie == 0xfeedbeef or message_type == 0x2:
    print("Received offer from " + server_ip_address + " attempting to connect...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((server_ip_address, server_tcp_port))
    sock.sendall(CLIENT_NICKNAME.encode())
    print(style.GREEN + sock.recv(MESSAGE_LENGTH).decode())
    listener = keyboard.Listener(on_press=pressed)
    listener.start()
    end = time.time() + TIME_TO_PLAY
    while time.time() < end:  # wait for input
        pass
    listener.stop()
    feedback = ""
    try:
        feedback = sock.recv(MESSAGE_LENGTH).decode()
    except:
        feedback = "\nServer Disconnected"
    print(feedback)
    sock.close()
    print("Server disconnected, listening for offer requests...")
