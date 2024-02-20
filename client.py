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


HOST = "127.0.0.1"
PORT = 65432
client_folder = 'client_dir/'


print("Hello! It a BSUIR network file manager")
name = ''
while name == '':
    print("Enter your name:", end = ' ')
    name = input()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    try:
        s.connect((HOST, PORT))
    
        # ------- SEND HI -------
        send_command(s, Commands.HI, [name])   
        code, args = recv_response(s)

        # ------- UNFINISHED UPLOAD -------
        #print("HI code " + str(code))   
        if code == ResponseCodes.UNFINISHED_UP.value:
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
                    time.sleep(1)
                    print("Second send")

        # ------- UNFINISHED DOWNLOAD -------
        if code == ResponseCodes.UNFINISHED_DOWN.value:
            print ("Found unfinished download")

            f_name = "client_dir/" + args[0]
            f_size = int(args[1])
            f_buff = int(args[2])
            curr_f_size = os.path.getsize(f_name)

            send_command(s, Commands.DOWNLOAD, [str(curr_f_size)])

            with open(f_name, 'ab') as file:
                #buffer_size = 64 * 1024
                proccesed_bytes = curr_f_size
                while proccesed_bytes < f_size:
                    data = s.recv(f_buff)
                    proccesed_bytes = proccesed_bytes + len(data)
                    file.write(data)
                    time.sleep(0.5)
                    print("Second download")
                send_command(s, Commands.DOWNLOAD, [])
        exit = 0
        
        if code != ResponseCodes.SUCCESS.value:
            print ("SERVER ERRROR")
            exit = 1

    except socket.error as err:
        print(f'Server Connection Error: {err}')
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
                    print (ret_code,ret_args)
                    continue
                with open(client_folder + splitted_input[1], "rb") as file:
                    buffer_size = 64 * 1024    #?????????????????????????????????????????????????????????????????????????????????????????
                    while True:
                        print(".", end='')
                        data = file.read(buffer_size)
                        if len(data) == 0: break
                        s.send(data)
                        time.sleep(0.5)
                    print('100%')
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

                with open(filename, 'wb') as file:
                    #buffer_size = 64 * 1024
                    proccesed_bytes = 0
                    while proccesed_bytes < f_size:
                        print(".", end='')
                        data = s.recv(f_buff)
                        proccesed_bytes = proccesed_bytes + len(data)
                        file.write(data)
                        time.sleep(0.5)
                    print('100%')
                    send_command(s, Commands.DOWNLOAD, []) #??????????????????????????????????????????????????????????????????????????/
        
        except socket.error as err:
            print(f'Error: {err}')
            exit = 1
        
    #print ("File manager is closed")