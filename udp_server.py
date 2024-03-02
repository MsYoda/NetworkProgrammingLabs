from random import randint
import socket
import struct
import time

from commands import Commands, ResponseCodes
from lib import recv, send

header_format = "I I I"

HOST = "127.0.0.1"
PORT = 65432


def recv_command(s: socket):
    command_bytes, addr = recv(s)
    if (len(command_bytes) == 0): raise ConnectionError('connection lost') # заменить на другое

    command = command_bytes[0]

    command_packet_parts = str(command_bytes, 'utf8').split('&')
    return command, command_packet_parts[1:len(command_packet_parts)], addr


def send_response(s : socket, addr, code : ResponseCodes, args : []):
    message = str(code.value) + '&' + '&'.join(args)
    send(s, addr, message.encode())



print("Hello! It a BSUIR network file manager server")

username = ''
filename = ''

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as conn:
    conn.bind((HOST, PORT))

    # print("Wait for message")
    # output, address = conn.recvfrom(128)
    # print(str(output, 'utf8'))

    while True:
        command = 0
        args = []
        addr = ""
        try:
            print('recv_command')
            command, args, addr = recv_command(conn)
        except ConnectionError as e:
            print("May be ACK")
  
        if command == Commands.ECHO.value:
            try:
                print(f'ECHO from {username}: {args[0]}')
                print('send_response')
                send_response(conn, addr, ResponseCodes.SUCCESS, [args[0]])
            except IndexError as e:
                print(f'{username} caused {e} when retry to download {filename}')
                #send_response(conn, ResponseCodes.ERROR, ['bad arguments'])
        #print(command)
