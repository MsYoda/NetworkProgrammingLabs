import shlex
import socket
import struct

from commands import Commands
from lib import recv, send



AN = 0
SN = 0

HOST = "127.0.0.1"
PORT = 65432
            

def get_bytes_of_command(command : Commands, args : []) -> bytes:
    return int(command.value).to_bytes(1, 'big') + bytes('&' + '&'.join(args), encoding='utf8')

def send_command(s : socket, target_addr, command : Commands, args : []):
    message = get_bytes_of_command(command, args)
    send(s, target_addr, message)

def recv_response(s : socket):
    response, addr = recv(s)
    response_parts = str(response, 'utf8').split('&')
    return int(response_parts[0]), response_parts[1:len(response_parts)]

def get_code(command : str) -> Commands:
    #if command == 'HI':
    #    return Commands.HI
    if command == 'ECHO':
        return Commands.ECHO
    if command == 'QUIT':
        return Commands.QUIT
    if command == 'TIME':
        return Commands.TIME
    if command == 'UPLOAD':
        return Commands.UPLOAD
    if command == 'DOWNLOAD':
        return Commands.DOWNLOAD
    if command == 'LIST':
        return Commands.LIST


with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    data = "Hello Server"
    #s.sendto(data.encode(), ((HOST, PORT)))
    exit = False
    while not exit:
        print(">", end=' ')
        user_input = input()
        if user_input == '':
            continue

        splitted_input = shlex.split(user_input)
        command = get_code(splitted_input[0])

        if command == Commands.ECHO:
            #send_command(s, (HOST, PORT), Commands.LIST, ['Hello there'])
            print('send_command')
            send_command(s, (HOST,PORT), Commands.ECHO, ['Hello server'])
            print('recv_response')
            code, args = recv_response(s)
            print(f"From server: {code} {args}")
        if command == Commands.QUIT:  
            exit = True


