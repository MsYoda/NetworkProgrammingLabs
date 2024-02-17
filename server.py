from datetime import datetime
import os

import socket

from commands import Commands, ResponseCodes

HOST = "127.0.0.1"
PORT = 65432

print("Hello! It a BSUIR network file manager server")

def recv_command(s):
    length = conn.recv(4)
    if (len(length) == 0): raise Exception()

    command_len = int.from_bytes(length, 'big')

    command_bytes = conn.recv(command_len)
    if (len(command_bytes) == 0): raise Exception()

    command = command_bytes[0]

    command_packet_parts = str(command_bytes, 'utf8').split('&')
    return command, command_packet_parts[1:len(command_packet_parts)]

def send_response(s : socket, code : ResponseCodes, args : []):
    message = str(code.value) + '&' + '&'.join(args)
    s.send(len(message).to_bytes(4, 'big'))
    s.sendall(bytes(message, encoding='utf8'))

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    username = ""
    filename = ""
    isUpload = False
    file_size = 0

    s.bind((HOST, PORT))
    s.listen()
    while True:
        print("Wait for client...")
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                command = 0
                args = []
                try: 
                    command, args = recv_command(s)
                except:
                    break

                if command == Commands.HI.value:
                    if args[0] == username and file_size != 0:
                        if isUpload:
                            proccesed_bytes = os.path.getsize('server_files/' + filename)
                            send_response(conn, ResponseCodes.UNFINISHED_UP, [filename, str(proccesed_bytes)])
                            try:
                                with open('server_files/' + filename, 'ab') as file:
                                    buffer_size = 64 * 1024
                                    while proccesed_bytes < file_size:
                                        data = conn.recv(buffer_size)
                                        if (len(data) == 0): 
                                            file.close()
                                            raise Exception()
                                        proccesed_bytes = proccesed_bytes + len(data)
                                        file.write(data)
                                filename = ''
                                file_size = 0
                                isUpload = False
                            except:
                                print("File dont UPLOADed with success")

                    else:
                        username = args[0]
                        send_response(conn, ResponseCodes.SUCCESS, []) 

                if command == Commands.ECHO.value:
                    send_response(conn, ResponseCodes.SUCCESS, [args[0]])

                if command == Commands.TIME.value:
                    now = datetime.now().time()
                    send_response(conn, ResponseCodes.SUCCESS, [str(now.hour), str(now.minute), str(now.second)])
                    
                if command == Commands.QUIT.value:
                    send_response(conn, ResponseCodes.SUCCESS, [])
                    break

                if command == Commands.LIST.value:
                    files = []
                    for file in os.listdir('server_files/'):
                        files.append(file)
                    send_response(conn, ResponseCodes.SUCCESS, files)

                if command == Commands.DOWNLOAD.value:
                    filename = args[0]
                    f_size = os.path.getsize(filename)
                    proccesed_bytes = 0
                    with open('server_files/' + filename, "rb") as file:
                        buffer_size = 64 * 1024
                        send_response(conn, ResponseCodes.SUCCESS, [str(f_size), str(buffer_size)])
                        while True:
                            data = file.read(buffer_size)
                            if len(data) == 0: break
                            conn.send(data)
                    filename = ''
                    file_size = 0

                if command == Commands.UPLOAD.value:
                    filename = args[0]
                    file_size = int(args[1])
                    proccesed_bytes = 0
                    isUpload = True
                    try:
                        with open('server_files/' + filename, 'wb') as file:
                            buffer_size = 64 * 1024
                            proccesed_bytes = 0
                            send_response(conn, ResponseCodes.SUCCESS, [])
                            while proccesed_bytes < file_size:
                                data = conn.recv(buffer_size)
                                if (len(data) == 0): 
                                    file.close()
                                    raise Exception()
                                proccesed_bytes = proccesed_bytes + len(data)
                                file.write(data)
                        filename = ''
                        file_size = 0
                        isUpload = False
                    except:
                        print("File dont UPLOADed with success")






                       
                    

                

            

    