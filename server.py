import random
import socket
import os
import time
import struct
from threading import Thread
from scapy.arch import get_if_addr

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
TCP_PORT = 2026
MESSAGE_LENGTH = 1024
TIME_TO_CONNECT = 10  # seconds
TIME_TO_PLAY = 10  # seconds

"""
method: make_bytes_message
purpose: makes the packet in the right format
"""


def make_bytes_message():
    return struct.pack('LBH', 0xfeedbeef, 0x2, TCP_PORT)


"""
method: send_broadcast
purpose: sends messages via UDP
"""


def send_broadcast():
    ip_address = get_if_addr("eth1")
    message = "Server started, listening on IP address " + ip_address
    sock = socket.socket(socket.AF_INET,  # Internet
                         socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    print(style.CYAN + message)
    t_end = time.time() + TIME_TO_CONNECT  # the time to wait for players
    while True:
        if time.time() < t_end:
            send_bytes = make_bytes_message()
            sock.sendto(send_bytes, (UDP_IP, UDP_PORT))
            time.sleep(1)  # wait 1 sec
        else:
            break


"""
method: connect_clients
purpose: accepts new players
"""


def connect_clients(connection_client, sock):
    t_end = time.time() + TIME_TO_CONNECT  # the time to wait for players
    sock.settimeout(t_end - time.time())
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


"""
method: generate_teams
purpose: divide connections into two random groups
"""


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


"""
method: get_group_names
purpose: returns string of the names of group's participants
"""


def get_group_names(group):
    names = ""
    for c in group.keys():
        try:
            names += c.recv(MESSAGE_LENGTH).decode() + "\n"
        except:
            pass
    return names


"""
method: generate_begin_message
purpose: returns the begin message of the game
"""


def generate_begin_message(namesA, namesB):
    begin_message = "Welcome to Keyboard Spamming Battle Royale.\nGroup 1:\n==\n"
    begin_message += namesA
    begin_message += "\nGroup 2:\n==\n"
    begin_message += namesB
    return begin_message


"""
method: send_message_to_group
purpose: send the message to group (if the group still connected)
"""


def send_message_to_group(message, group):
    for c in group.keys():
        try:
            c.sendall(message)
        except:
            pass


"""
method: send_message
purpose: send the message to groups
"""


def send_message(begin_message, groupA, groupB):
    begin_message = begin_message.encode()
    send_message_to_group(begin_message, groupA)  # Group A
    send_message_to_group(begin_message, groupB)  # Group B


"""
method: total_messages
purpose: returns all chars that were sent from group
"""


def total_messages(group):
    m = ""
    for c in group.keys():
        try:
            c.settimeout(0)
            m += c.recv(MESSAGE_LENGTH).decode()
        except:
            pass
    return m


"""
method: most_common_ch
purpose: STATISTICS BONUS FEATURE - returns the char that apeared the most in the given message
"""


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


"""
method: generate_end_message
purpose: generate an end message including STATISTICS FEATURE
"""


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
            end_message += style.RED + "\nSTATISTICS:\n"
            end_message += style.CYAN
            end_message += "\nThe most common char of Group 1 Is: " + str(
                common_ch_A[0]) + " and it is appears: " + str(
                common_ch_A[1]) + " times.\n"
    elif countB > countA:
        end_message += "Group 2 wins!\nCongratulations to the winners:\n==\n"
        end_message += namesB
        if common_ch_B[1] > 0:
            end_message += style.RED + "\nSTATISTICS:\n"
            end_message += style.CYAN
            end_message += "\nThe most common char of Group 2 Is: " + str(
                common_ch_B[0]) + " and it is appears: " + str(
                common_ch_B[1]) + " times.\n"
    else:
        end_message += "Draw!\nCongratulations to the winners:\n==\n"
        end_message += namesA
        end_message += namesB
        if common_ch_A[1] > 0:
            end_message += style.RED + "\nSTATISTICS:\n"
            end_message += style.CYAN
            end_message += "\nThe most common char of Group 1 Is: " + str(
                common_ch_A[0]) + " and it is appears: " + str(
                common_ch_A[1]) + " times.\n"
            end_message += "\nThe most common char of Group 2 Is: " + str(
                common_ch_B[0]) + " and it is appears: " + str(
                common_ch_B[1]) + " times.\n"
    return end_message


"""
method: start_game
purpose: play the game
"""


def start_game(connection_client, sock):
    groupA = {}
    groupB = {}
    generate_teams(connection_client, groupA, groupB)  # make random groups
    namesA = get_group_names(groupA)
    namesB = get_group_names(groupB)
    begin_message = generate_begin_message(namesA, namesB)  # generate begin message
    send_message(begin_message, groupA, groupB)
    time.sleep(TIME_TO_PLAY)  # waits for players to play
    end_message = generate_end_message(groupA, groupB, namesA, namesB)  # generate end message
    print(end_message)
    send_message(end_message, groupA, groupB)


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # init the TCP socket
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    ip_address = get_if_addr("eth1")
    sock.bind(('', TCP_PORT))
    sock.listen(1)
    while True:
        time.sleep(1)  # reduce CPU preformence
        connection_client = {}
        broadcaster = Thread(target=send_broadcast, args=())  # send broadcast for players
        client_connector = Thread(target=connect_clients, args=(connection_client, sock,))  # accepts new players
        broadcaster.start()
        client_connector.start()
        broadcaster.join()
        client_connector.join()
        start_game(connection_client, sock)  # play the game
        print(style.BLUE + "Game over, sending out offer requests...")  # game session over


if __name__ == "__main__":
    main()
