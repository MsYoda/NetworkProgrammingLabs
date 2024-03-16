from random import randint
import socket
import struct
import time
from datetime import datetime
import os
import traceback

from commands import Commands, ResponseCodes
from lib import recv, recv_large, send, send_large

header_format = "I I I"

HOST = "192.168.100.66"
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

def send_file(s, filename, filesize, addr, offset = 0):
    recv_command(s)
    with open(filename, "rb") as file:
        file.seek(offset)
        buffer_size = 64500 * 100
        proccesed_bytes = offset
        while True:
            data = file.read(buffer_size)
            if len(data) == 0: break

            #sended = conn.send(data)
            send_large(conn, addr, data)

            #conn.sendto(data, addr)

            #if sended == 0: break
            proccesed_bytes = proccesed_bytes + buffer_size
            #time.sleep(0.2)

    recv_command(conn)

def recv_file(s, filename, file_size, offset = 0):
    mode = 'wb'
    if offset > 0: mode = 'ab'
    proccesed_bytes = offset

    with open(filename, mode) as file:
        buffer_size = 64 * 1024
        while proccesed_bytes < file_size:
            #data = conn.recv(buffer_size)
            data = recv_large(conn, buffer_size // 16, buffer_size)
            if (len(data) == 0): 
                file.close()
                raise ConnectionError('connection lost')
            proccesed_bytes = proccesed_bytes + len(data)
            file.write(data)


print("Hello! It a BSUIR network file manager server")

username = ""
filename = ""
isUpload = False
file_size = 0

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as conn:

    def clear_state():
        global filename
        global isUpload
        global file_size

        filename = ""
        isUpload = False
        file_size = 0

    conn.bind((HOST, PORT))

    # print("Wait for message")
    # output, address = conn.recvfrom(128)
    # print(str(output, 'utf8'))

    while True:
        print("Wait for client...")
        command = 0
        args = []
        addr = ""
        try:
            print('recv_command')
            command, args, addr = recv_command(conn)
        except ConnectionError as e:
            print("May be ACK")
  

        if command == Commands.HI.value:
            try:
                print(f'Hi from {username}')
                print('send_response')
                send_response(conn, addr, ResponseCodes.SUCCESS, [args[0]])
            except IndexError as e:
                print(f'{username} caused {e} when retry to download {filename}')

        if command == Commands.ECHO.value:
            try:
                print(f'ECHO from {username}: {args[0]}')
                print('send_response')
                send_response(conn, addr, ResponseCodes.SUCCESS, [args[0]])
            except IndexError as e:
                print(f'{username} caused {e} when retry to download {filename}')
                #send_response(conn, ResponseCodes.ERROR, ['bad arguments'])

        if command == Commands.TIME.value:
            print(f'TIME from {username}')
            now = datetime.now().time()
            send_response(conn, addr, ResponseCodes.SUCCESS, [str(now.hour), str(now.minute), str(now.second)])
        
        # После send_response сделай recv_large
        if command == Commands.LIST.value:
            print(f'LIST from {username}')
            files = []
            for file in os.listdir('server_files/'):
                files.append(file)
            send_response(conn, addr, ResponseCodes.SUCCESS, files)
            data = recv_large(conn, 5, 24)
            print(f'Data from recv_large: {data}')

        if command == Commands.QUIT.value:
            print(f'QUIT from {username}')
            send_response(conn, addr, ResponseCodes.SUCCESS, [])
            break
        
        if command == Commands.DOWNLOAD.value:
            try:
                isUpload = False

                filename = args[0]
                file_size = os.path.getsize('server_files/' + filename)

                print(f'DOWNLOAD {filename} from {username}')

                send_response(conn, addr, ResponseCodes.SUCCESS, [str(file_size), str(64500 * 100)])
                send_file(conn, 'server_files/' + filename, file_size, addr)

                print(f'Server succesfully send file to {username}')
            except (FileNotFoundError, FileExistsError) as e:
                print(f'{username} caused {e} when try to download {filename}')
                send_response(conn, ResponseCodes.ERROR, [filename, 'dont exsist'])
                
            except (ValueError, IndexError) as e:
                print(f'{username} caused {e} when try to download {filename}')
                send_response(conn, ResponseCodes.ERROR, ['bad arguments'])
                
            except ConnectionError as e:
                print(f'{username} caused {e} when try to download {filename}') 
                traceback.print_exc()
            except Exception as e:
                print(f'{username} caused {e} when try to download {filename}') 
                traceback.print_exc()
                


        #print(command)
