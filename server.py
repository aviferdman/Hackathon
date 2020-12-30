import random
import socket
import os
import time
import struct
from threading import Thread
import requests


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
TCP_PORT = 5031
MESSAGE_LENGTH = 1024
TIME_TO_CONNECT = 10  # seconds
TIME_TO_PLAY = 10  # seconds
c_A = []
c_B = []


def make_bytes_message():
    return struct.pack('LBH', 0xfeedbeef, 0x2, TCP_PORT)


def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]





def send_broadcast():
    hostname = socket.gethostname()  # getting the hostname by socket.gethostname() method
    ip_address = get_ip_address()
    #ip_address = socket.gethostbyname(hostname)
    #   bytes_ip_address = ip_address.encode()
    message = "Server started, listening on IP address " + ip_address
    sock = socket.socket(socket.AF_INET,  # Internet
                         socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    print(style.CYAN + message)
    t_end = time.time() + TIME_TO_CONNECT
    while True:
        if time.time() < t_end:
            send_bytes = make_bytes_message()
            sock.sendto(send_bytes, (UDP_IP, UDP_PORT))
            time.sleep(1)
        else:
            break
    # sock.shutdown(socket.SHUT_RDWR)


def connect_clients(connection_client, sock):
    t_end = time.time() + TIME_TO_CONNECT
    sock.settimeout(t_end - time.time())  # accept is waiting for no mare than time left to connect
    while True:
        if time.time() < t_end:
            try:
                connection, client_address = sock.accept()
                connection_client[connection] = client_address
                print(style.GREEN + "New player connected")
            except:
                print("Time is up for connecting new players")
        else:
            break
    # sock.shutdown(socket.SHUT_RDWR)


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
            names += c.recv(MESSAGE_LENGTH).decode()+"\n"
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


def total_messages(group):
    m = ""
    for c in group.keys():
        try:
            c.settimeout(0)
            m += c.recv(MESSAGE_LENGTH).decode()
        except:
            pass
    return m


def most_common_ch(message):
    commons = {}
    for c in message:
        commons[c] = commons.get(c, 0) + 1
    maxAppearance = 0
    maxCh = ''
    for ch in commons.keys():
        if commons[ch] > maxAppearance:
            maxAppearance = commons[ch]
            maxCh = ch
    return [maxCh, maxAppearance]


def generate_end_message(groupA, groupB, namesA, namesB):
    messageA = total_messages(groupA)
    messageB = total_messages(groupB)
    countA = len(messageA)
    countB = len(messageB)
    common_ch_A = most_common_ch(messageA)
    common_ch_B = most_common_ch(messageB)
    end_message = "Game over!\nGroup 1 typed in " + str(countA) + " characters. Group 2 typed in " + str(
        countB) + " characters.\n"
    if countA > countB:
        end_message += "Group 1 wins!\nCongratulations to the winners:\n==\n"
        end_message += namesA
        if common_ch_A[1] > 0:
            end_message += "\nThe most common char of Group 1 Is: " + str(common_ch_A[0]) + " and it is appears: " + str(
                common_ch_A[1]) + " times."
    elif countB > countA:
        end_message += "Group 2 wins!\nCongratulations to the winners:\n==\n"
        end_message += namesB
        if common_ch_B[1] > 0:
            end_message += "\nThe most common char of Group 2 Is: " + str(common_ch_B[0]) + " and it is appears: " + str(
                common_ch_B[1]) + " times."
    else:
        end_message += "Draw!\nCongratulations to the winners:\n==\n"
        end_message += namesA
        end_message += namesB
        if common_ch_A[1] > 0:
            end_message += "\nThe most common char of Group 1 Is: " + str(common_ch_A[0]) + " and it is appears: " + str(
                common_ch_A[1]) + " times."
            end_message += "\nThe most common char of Group 2 Is: " + str(common_ch_B[0]) + " and it is appears: " + str(
                common_ch_B[1]) + " times."
    return end_message


def close_connections (group):
    for c in group.keys():
        c.close()




def start_game(connection_client, sock):
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
    print(end_message)
    send_message(end_message, groupA, groupB)
    # close_connections(groupA)
    # close_connections(groupB)


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # bind the socket to a public host, and a well-known port
    # sock.bind((socket.gethostbyname(socket.gethostname()), TCP_PORT))
    # become a server socket
    sock.bind(("127.0.1.1", TCP_PORT))
    sock.listen(1)
    while True:
        connection_client = {}
        broadcaster = Thread(target=send_broadcast, args=())
        client_connector = Thread(target=connect_clients, args=(connection_client, sock,))
        broadcaster.start()
        client_connector.start()
        broadcaster.join()
        client_connector.join()
        start_game(connection_client, sock)
        print(style.BLUE+"Game over, sending out offer requests...")
        


if __name__ == "__main__":
    main()