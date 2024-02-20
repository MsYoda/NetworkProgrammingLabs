import socket
import shlex
import os
import time
from datetime import datetime 

from commands import Commands
from commands import ResponseCodes

TCP_KEEPALIVE = 16

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
         
    return Commands.NOTCOMMAND

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
            print(".", end='', flush=True) 
            data = s.recv(f_buff)
            proccesed_bytes = proccesed_bytes + len(data)
            file.write(data)
        time_end = time.time()
        print (f'100% \nAverage Download Speed:{((f_size - data_size)/(time_end - time_start)/1000):.2f}KB/sec')
    send_command(s, Commands.DOWNLOAD, []) 

HOST = "192.168.43.188" #"127.0.0.1"
PORT = 65432
client_folder = 'client_dir/'


print("Hello! It a BSUIR network file manager")
name = ''
while name == '':
    print("Enter your name:", end = ' ')
    name = input()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    try:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 5)  # Время ожидания перед первым keep-alive
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 5)  # Интервал между последующими keep-alive
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 3)

        s.connect((HOST, PORT))
    
        # ------- SEND HI -------
        send_command(s, Commands.HI, [name])   
        code, args = recv_response(s)

        # ------- UNFINISHED UPLOAD -------
        #print("HI code " + str(code))   
        if code == ResponseCodes.UNFINISHED_UP.value:
            print ("Found Unfinished Upload")

            f_name = client_folder + args[0]
            bytes_have = int(args[1])

            if not os.path.isfile(f_name):
                print (f'Unfinished upload refused')
                print (f'File "{f_name}" does not exist')
                send_command(s, Commands.CLIENTERROR, [])
            else:
                send_command(s, Commands.UPLOAD, [])
                upload_file(f_name, s, bytes_have)
            code = ResponseCodes.SUCCESS.value

        # ------- UNFINISHED DOWNLOAD -------
        if code == ResponseCodes.UNFINISHED_DOWN.value:
            try:
                print ("Found Unfinished Download")

                f_name = "client_dir/" + args[0]
                f_size = int(args[1])
                f_buff = int(args[2])
                curr_f_size = os.path.getsize(f_name)

                send_command(s, Commands.DOWNLOAD, [str(curr_f_size)])
                
                download_file(f_name, 'ab', curr_f_size, f_size, f_buff)
                code = ResponseCodes.SUCCESS.value
            except (FileNotFoundError, FileExistsError) as e:
                send_command(s, Commands.CLIENTERROR, [])
                print("Unfinished download refused")
                print (f'File "{f_name}" does not exist')
                code = ResponseCodes.SUCCESS.value

        exit = 0
        
        if code != ResponseCodes.SUCCESS.value:
            print ("SERVER ERRROR")
            exit = 1

    except socket.error as err:
        print(f'\nServer Connection Error: {err}')
        exit = 1    

    while not exit:
        print(">", end=' ')
        user_input = input()
        if user_input == '':
            continue

        splitted_input = shlex.split(user_input)
        #print (splitted_input)
        command = get_code(splitted_input[0])
        if command == Commands.NOTCOMMAND:
            print ("Incorrect Command Input")
            continue

        try: 
            # --- QUIT ---
            if command == Commands.QUIT:
                if len(splitted_input) > 1:
                    print("Wrong Arguments")
                    continue
                send_command(s, Commands.QUIT, [])
                ret_code,ret_args = recv_response(s)
                break

            # --- ECHO ---
            if command == Commands.ECHO:
                if len(splitted_input) < 2:
                    print("Wrong Arguments")
                    continue
                send_command(s, command, [user_input[5:]])
                ret_code,ret_args = recv_response(s)
                print(ret_args[0])
                continue 
            
            # --- TIME ---
            if command == Commands.TIME:
                if len(splitted_input) > 1:
                    print("Wrong Arguments")
                    continue
                send_command(s, command, [])
                ret_code,ret_args = recv_response(s)
                print('Current Server Time is ' + ':'.join(ret_args))
                continue 

            # --- LIST ---
            if command == Commands.LIST:
                if len(splitted_input) > 1:
                    print("Wrong Arguments")
                    continue
                send_command(s, command, [])
                ret_code,ret_args = recv_response(s)
                for arg in ret_args:
                    print(f"- {arg}")
                continue

            # --- UPLOAD ---
            if command == Commands.UPLOAD:
                if len(splitted_input) != 2:
                    print("Wrong Arguments")
                    continue
                if not os.path.isfile(client_folder + splitted_input[1]):
                    print (f'File "{client_folder + splitted_input[1]}" does not exist')
                    continue 
                #print ("exist")
                f_size = os.path.getsize(client_folder + splitted_input[1])
                splitted_input.append(str(f_size))

                send_command(s, command, splitted_input[1:len(splitted_input)])
                ret_code,ret_args = recv_response(s)

                if ret_code == ResponseCodes.ERROR.value:
                    print(f'Error. File "{ret_args[0]}" {ret_args[1]}')
                    continue 
                
                upload_file(client_folder + splitted_input[1], s, 0)
                continue 

            # --- DOWNLOAD ---
            if command == Commands.DOWNLOAD:
                #print ("Started download")
                if len(splitted_input) != 2:
                    print("Wrong Arguments")
                    continue

                send_command(s, command, splitted_input[1:len(splitted_input)])
                ret_code,ret_args = recv_response(s)
                #print("Code: " + str(code))
                #print(ret_args)
                if ret_code == ResponseCodes.ERROR.value:
                    print(f'Error. File "{ret_args[0]}" {ret_args[1]}')
                    continue                   
                
                filename = client_folder + splitted_input[1]
                f_size = int(ret_args[0])
                f_buff = int(ret_args[1])

                download_file(filename, 'wb', 0, f_size, f_buff)

        
        except socket.error as err:
            print(f'\nError: {err}')
            exit = 1
        
    #print ("File manager is closed")