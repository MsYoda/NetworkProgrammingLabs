import shlex
import socket
import struct
import os
import time
from datetime import datetime 

from commands import Commands
from lib import recv, send

from commands import ResponseCodes
TCP_KEEPALIVE = 16

AN = 0
SN = 0

HOST = "127.0.0.1"
PORT = 65432
client_folder = 'client_dir/'            

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


def upload_file(f_name: str, s: socket, seek_offset: int):
    time_start = time.time()
    data_size = 0
    with open(f_name, "rb") as file:
        file.seek(seek_offset)
        buffer_size = 64 * 1024    
        while True:               
            print(".", end='', flush=True)
            data = file.read(buffer_size)
            if len(data) == 0: break
            s.send(data)
            data_size = data_size + len(data)
            # time.sleep(0.5)
        time_end = time.time()
        print (f'100% \nAverage Upload Speed:{(data_size/(time_end - time_start)/1000):.2f}KB/sec') 


def download_file(filename: str, file_mode: str, proccesed_bytes: int, f_size: int, f_buff: int):
    with open(filename, file_mode) as file:
        #buffer_size = 64 * 1024
        # proccesed_bytes = 0
        time_start = time.time()
        data_size = proccesed_bytes
        while proccesed_bytes < f_size:
            print(".", end='') # , flush=True) 
            data = s.recv(f_buff)
            proccesed_bytes = proccesed_bytes + len(data)
            file.write(data)
        time_end = time.time()
        print (f'100% \nAverage Download Speed:{((f_size - data_size)/(time_end - time_start)/1000):.2f}KB/sec')
    send_command(s, Commands.DOWNLOAD, []) 




print("Hello! It a BSUIR network file manager")
name = ''
while name == '':
    print("Enter your name:", end = ' ')
    name = input()

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:

    # ------- SEND HI -------
    send_command(s, (HOST,PORT), Commands.HI, [name])   
    code, args = recv_response(s)
    print(f"From server: {code} {args}")

    exit = False
    while not exit:
        print(">", end=' ')
        user_input = input()
        if user_input == '':
            continue

        splitted_input = shlex.split(user_input)
        command = get_code(splitted_input[0])
        if command == Commands.NOTCOMMAND:
            print ("Incorrect Command Input")
            continue


        # --- QUIT ---
        if command == Commands.QUIT:
            if len(splitted_input) > 1:
                print("Wrong Arguments")
                continue
            send_command(s, (HOST,PORT), Commands.QUIT, [])
            ret_code,ret_args = recv_response(s)
            break

        # --- ECHO ---
        if command == Commands.ECHO:
            if len(splitted_input) < 2:
                print("Wrong Arguments")
                continue
            send_command(s, (HOST,PORT), command, [user_input[5:]])
            ret_code,ret_args = recv_response(s)
            print(ret_args[0])
            continue 
            # #send_command(s, (HOST, PORT), Commands.LIST, ['Hello there'])
            # print('send_command')
            # send_command(s, (HOST,PORT), Commands.ECHO, ['Hello server'])
            # print('recv_response')
            # code, args = recv_response(s)
            # print(f"From server: {code} {args}")

        # --- TIME ---
        if command == Commands.TIME:
            if len(splitted_input) > 1:
                print("Wrong Arguments")
                continue
            send_command(s, (HOST,PORT), command, [])
            ret_code,ret_args = recv_response(s)
            print('Current Server Time is ' + ':'.join(ret_args))
            continue 

        # --- LIST ---
        # После recv_response сделай send_large каких нибудь данных (блольших)
        if command == Commands.LIST:
            if len(splitted_input) > 1:
                print("Wrong Arguments")
                continue
            send_command(s, (HOST,PORT), command, [])
            ret_code,ret_args = recv_response(s)
            for arg in ret_args:
                print(f"- {arg}")
            continue
        




