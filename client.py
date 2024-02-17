import socket
import shlex
import os
import time

from commands import Commands
from commands import ResponseCodes

def get_bytes_of_command(command : Commands, args : []) -> bytes:
    return int(command.value).to_bytes(1, 'big') + bytes('&' + '&'.join(args), encoding='utf8')

def send_command(s : socket, command : Commands, args : []):
    message = get_bytes_of_command(command, args)
    s.send(len(message).to_bytes(4, 'big'))
    s.sendall(message)

def recv_response(s : socket):
    response_len = int.from_bytes(s.recv(4), 'big')
    response_parts = str(s.recv(response_len), 'utf8').split('&')
    return int(response_parts[0]), response_parts[1:len(response_parts)]

def get_code(command : str) -> Commands:
    if command == 'HI':
        return Commands.HI
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
         
    return Commands.NOTCOMMAND

HOST = "127.0.0.1"
PORT = 65432

print("Hello! It a BSUIR network file manager")
print("Enter your name:")
name = input()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    send_command(s, Commands.HI, [name])
    code, args = recv_response(s)

    print("HI code " + str(code))
    if int(recv_response[0]) == ResponseCodes.UNFINISHED_UP:
        print ("Found unfinished upload")

        f_name = "client_dir/" + args[0]
        bytes_have = int(args[1])

        with open(f_name, "rb") as file:
            file.seek(bytes_have)
            buffer_size = 64 * 1024
            while True:
                data = file.read(buffer_size)
                if len(data) == 0: break
                s.send(data)


    if int(recv_response[0]) == ResponseCodes.UNFINISHED_DOWN:
        print ("Found unfinished download")



    exit = 0

    while not exit:
        print("Enter comand:")
        user_input = input()
        if user_input == 'QUIT':
            # отправить QUIT
            exit = 1

        splitted_input = shlex.split(user_input)
        print (splitted_input)

        command = get_code(splitted_input[0])

        f_size: int
        if command == Commands.UPLOAD:
            splitted_input[1] = "client_dir/" + splitted_input[1]
            f_size = os.path.getsize(splitted_input[1])
            print ("file size: " + str(f_size))
            splitted_input.append(str(f_size))

        if command == Commands.DOWNLOAD:
            print ("Started download")


        send_command(s, command, splitted_input[1:len(splitted_input)])
        ret_code,ret_args = recv_response(s)
        print("Code: " + str(code))
        print(ret_args)

        # UPLOAD
        if command == Commands.UPLOAD and ret_code == ResponseCodes.SUCCESS.value:
            with open(splitted_input[1], "rb") as file:
                buffer_size = 64 * 1024
                while True:
                    data = file.read(buffer_size)
                    if len(data) == 0: break
                    s.send(data)
                    time.sleep(3)

        # DOWNLOAD
        if command == Commands.DOWNLOAD and ret_code == ResponseCodes.SUCCESS.value:
            filename = 'client_dir/' + splitted_input[1]
            f_size = int(ret_args[0])
            f_buff = int(ret_args[1])

            with open(filename, 'wb') as file:
                # buffer_size = 64 * 1024
                proccesed_bytes = 0
                while proccesed_bytes < f_size:
                    data = s.recv(f_buff)
                    proccesed_bytes = proccesed_bytes + len(data)
                    file.write(data)