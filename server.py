import socket


HOST = "127.0.0.1"
PORT = 65432

print("Hello! It a BSUIR network file manager server")


# Создание сокета и отправка имени серверу
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print(f"Connected by {addr}")
        while True:
           command_len = int.from_bytes(conn.recv(4), 'big')
           print(command_len)
           cc = str(conn.recv(command_len), 'utf8').split(' ')
           break

    