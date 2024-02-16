from datetime import datetime

import socket

from commands import Commands, ResponseCodes

HOST = "127.0.0.1"
PORT = 65432

print("Hello! It a BSUIR network file manager server")

def recv_command(s):
    command_len = int.from_bytes(conn.recv(4), 'big')
    command_bytes = conn.recv(command_len)
    command = command_bytes[0]

    command_packet_parts = str(command_bytes, 'utf8').split('&')
    return command, command_packet_parts[1:len(command_packet_parts)]

def send_response(s : socket, code : ResponseCodes, args : []):
    message = str(code.value) + '&' + '&'.join(args)
    s.send(len(message).to_bytes(4, 'big'))
    s.sendall(bytes(message, encoding='utf8'))

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    username = ""

    s.bind((HOST, PORT))
    s.listen()
    while True:
        print("Wait for client...")
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                command, args = recv_command(s)

                if command == Commands.HI.value:
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
                

            

    