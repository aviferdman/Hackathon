import socket
import os
import time
import sys

os.system("")

UDP_PORT = 5005
SERVER_TCP_PORT = 5006
MESSAGE_LENGTH = 1024
CLIENT_NICKNAME = "RAK BIBI\n"
TIME_TO_PLAY = 10  # seconds


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


def main():
    print(style.YELLOW + "Client started, listening for offer requests...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind(("0.0.0.0", UDP_PORT))
    data, address = sock.recvfrom(MESSAGE_LENGTH)
    sock.close()
    server_ip_address = data.decode()
    print("Received offer from " + server_ip_address + " attempting to connect...")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((server_ip_address, SERVER_TCP_PORT))
    sock.sendall(CLIENT_NICKNAME.encode())
    print(style.GREEN + sock.recv(MESSAGE_LENGTH).decode())

    end = time.time() + TIME_TO_PLAY
    while time.time() < end:  # wait for input
        pass
    # TODO: understand how to send without enter at the end
    sock.sendall(b"a")
    print(sock.recv(MESSAGE_LENGTH).decode())


if __name__ == "__main__":
    main()
