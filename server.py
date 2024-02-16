import socket


from commands import Commands

HOST = "127.0.0.1"
PORT = 65432

print("Hello! It a BSUIR network file manager server")

def recv_command(s):
    command_len = int.from_bytes(conn.recv(4), 'big')
    command_bytes = conn.recv(command_len)
    command = command_bytes[0]

    command_packet_parts = str(command_bytes, 'utf8').split('&')
    return command, command_packet_parts[1:len(command_packet_parts)]

def send_response(s : socket, args : []):
    message = '&'.join(args)
    s.send(len(message).to_bytes(4, 'big'))
    s.sendall(bytes(message, encoding='utf8'))

# Создание сокета и отправка имени серверу
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print(f"Connected by {addr}")
        while True:
            command, args = recv_command(s)

            if command == Commands.ECHO.value:
                send_response(conn, [args[0]])

            break

    