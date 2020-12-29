import random
import socket
import os
import time
import struct
from threading import Thread

os.system("")


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


UDP_IP = '<broadcast>'
UDP_PORT = 13117
TCP_PORT = 5006
MESSAGE_LENGTH = 1024
TIME_TO_CONNECT = 10  # seconds
TIME_TO_PLAY = 10  # seconds
c_A = []
c_B = []


def make_bytes_message():
    return struct.pack('LBH', 0xfeedbeef, 0x2, TCP_PORT)


def send_broadcast():
    hostname = socket.gethostname()  # getting the hostname by socket.gethostname() method
    ip_address = socket.gethostbyname(hostname)  # getting the IP address using socket.gethostbyname() method
    #   bytes_ip_address = ip_address.encode()
    message = "Server started, listening on IP address " + ip_address
    sock = socket.socket(socket.AF_INET,  # Internet
                         socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    print(style.CYAN + message)
    t_end = time.time() + TIME_TO_CONNECT
    while time.time() < t_end:
        send_bytes = make_bytes_message()
        sock.sendto(send_bytes, (UDP_IP, UDP_PORT))
        time.sleep(1)
    sock.close()


def connect_clients(connection_client, sock):
    t_end = time.time() + TIME_TO_CONNECT
    sock.settimeout(t_end - time.time())  # accept is waiting for no mare than time left to connect
    while time.time() < t_end:
        try:
            connection, client_address = sock.accept()
            connection_client[connection] = client_address
            print(style.GREEN + "New player connected")
        except:
            print("Time is up for connecting new players")
    sock.close()


def generate_teams(connection_client, groupA, groupB):
    original_size = len(connection_client)
    for i in range(original_size):
        key = random.choice(list(connection_client))
        value = connection_client[key]
        if i % 2 == 0:
            groupA[key] = value
        else:
            groupB[key] = value
        del connection_client[key]


def get_group_names(group):
    names = ""
    for c in group.keys():
        try:
            names += c.recv(MESSAGE_LENGTH).decode()
        except:
            pass
    return names


def generate_begin_message(namesA, namesB):
    begin_message = "Welcome to Keyboard Spamming Battle Royale.\nGroup 1:\n==\n"
    begin_message += namesA
    begin_message += "\nGroup 2:\n==\n"
    begin_message += namesB
    return begin_message


def send_message_to_group(message, group):
    for c in group.keys():
        try:
            c.sendall(message)
        except:
            pass


def send_message(begin_message, groupA, groupB):
    begin_message = begin_message.encode()
    send_message_to_group(begin_message, groupA)
    send_message_to_group(begin_message, groupB)


def count_characters(group):
    count = 0
    for c in group.keys():
        try:
            c.settimeout(0)
            message = c.recv(MESSAGE_LENGTH).decode()
            count += len(message)
        except:
            pass
    return count


def generate_end_message(groupA, groupB, namesA, namesB):
    countA = count_characters(groupA)
    countB = count_characters(groupB)
    end_message = "Game over!\nGroup 1 typed in " + str(countA) + " characters. Group 2 typed in " + str(
        countB) + " characters.\n"
    if countA > countB:
        end_message += "Group 1 wins!\nCongratulations to the winners:\n==\n"
        end_message += namesA
    elif countB > countA:
        end_message += "Group 2 wins!\nCongratulations to the winners:\n==\n"
        end_message += namesB
    else:
        end_message += "Draw!\nCongratulations to the winners:\n==\n"
        end_message += namesA
        end_message += namesB
    return end_message


def start_game(connection_client):
    groupA = {}
    groupB = {}
    generate_teams(connection_client, groupA, groupB)
    namesA = get_group_names(groupA)
    namesB = get_group_names(groupB)
    begin_message = generate_begin_message(namesA, namesB)
    send_message(begin_message, groupA, groupB)
    end = time.time() + TIME_TO_PLAY
    while time.time() < end:  # wait for input
        pass
    end_message = generate_end_message(groupA, groupB, namesA, namesB)
    send_message(end_message, groupA, groupB)


def main():
    while True:
        connection_client = {}
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # bind the socket to a public host, and a well-known port
        sock.bind((socket.gethostname(), TCP_PORT))
        # become a server socket
        sock.listen(5)
        broadcaster = Thread(target=send_broadcast, args=())
        client_connector = Thread(target=connect_clients, args=(connection_client, sock,))
        broadcaster.start()
        client_connector.start()
        broadcaster.join()
        client_connector.join()

        start_game(connection_client)
        print(style.BLUE+"Game over, sending out offer requests...")
        sock.close()


if __name__ == "__main__":
    main()