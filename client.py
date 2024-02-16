import socket

from commands import Commands

def get_bytes_of_command(command : Commands, args : []) -> bytes:
    return int(command.value).to_bytes(1, 'big') + bytes('&' + '&'.join(args), encoding='utf8')

def send_command(s : socket, command : Commands, args : []):
    message = get_bytes_of_command(command, args)
    s.send(len(message).to_bytes(4, 'big'))
    s.sendall(message)

def recv_response(s : socket) -> []:
    response_len = int.from_bytes(s.recv(4), 'big')
    response_parts = str(s.recv(response_len), 'utf8').split('&')
    return response_parts

HOST = "127.0.0.1"
PORT = 65432

print("Hello! It a BSUIR network file manager")
print("Enter your name:")
name = input()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    send_command(s, Commands.ECHO, [name])
    t = recv_response(s)
    print(t)
