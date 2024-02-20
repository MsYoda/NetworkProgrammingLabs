from datetime import datetime
import os

import socket

from commands import Commands, ResponseCodes

HOST = "127.0.0.1"
PORT = 65432

print("Hello! It a BSUIR network file manager server")

def recv_command(s):
    length = conn.recv(4)
    if (len(length) == 0): raise ConnectionError('connection lost')

    command_len = int.from_bytes(length, 'big')

    command_bytes = conn.recv(command_len)
    if (len(command_bytes) == 0): raise ConnectionError('connection lost')

    command = command_bytes[0]

    command_packet_parts = str(command_bytes, 'utf8').split('&')
    return command, command_packet_parts[1:len(command_packet_parts)]

def send_response(s : socket, code : ResponseCodes, args : []):
    message = str(code.value) + '&' + '&'.join(args)
    s.send(len(message).to_bytes(4, 'big'))
    s.sendall(bytes(message, encoding='utf8'))

def send_file(s, filename, filesize, offset = 0):
    with open(filename, "rb") as file:
        file.seek(offset)
        buffer_size = 64 * 1024
        proccesed_bytes = offset
        while True:
            data = file.read(buffer_size)
            if len(data) == 0: break

            sended = conn.send(data)
            if sended == 0: break
            proccesed_bytes = proccesed_bytes + sended

            percentage = (proccesed_bytes / file_size) * 100
            print(f'{percentage:.2f}%')

        recv_command(conn)

def recv_file(s, filename, file_size, offset = 0):
    mode = 'wb'
    if offset > 0: mode = 'ab'
    proccesed_bytes = offset

    with open(filename, mode) as file:
        buffer_size = 64 * 1024
        while proccesed_bytes < file_size:
            data = conn.recv(buffer_size)
            if (len(data) == 0): 
                file.close()
                raise ConnectionError('connection lost')
            proccesed_bytes = proccesed_bytes + len(data)
            file.write(data)

            percentage = (proccesed_bytes / file_size) * 100
            print(f'{percentage:.2f}%')

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
                except ValueError as e:
                    print(f'{username} caused {e} when recv_command')
                    send_response(conn, ResponseCodes.ERROR, ['bad arguments'])
                except ConnectionError as e:
                    print(f'{username} caused {e} when recv_command')
                    break 
                except Exception as e:
                    print(f'{username} caused {e} when when recv_command') 
                    break

                if command == Commands.HI.value:
                    if args[0] == username and file_size != 0:
                        if isUpload:
                            try:
                                proccesed_bytes = os.path.getsize('server_files/' + filename)
                                send_response(conn, ResponseCodes.UNFINISHED_UP, [filename, str(proccesed_bytes)])

                                recv_file(conn, 'server_files/' + filename, file_size, proccesed_bytes)

                                filename = ''
                                file_size = 0
                                isUpload = False
                            except (FileNotFoundError, FileExistsError) as e:
                                print(f'{username} caused {e} when retry to upload {filename}')
                                send_response(conn, ResponseCodes.ERROR, [filename, 'dont exsist'])
                                filename = ''
                                file_size = 0
                                isUpload = False
                            except (ValueError, IndexError) as e:
                                print(f'{username} caused {e} when retry to upload {filename}')
                                send_response(conn, ResponseCodes.ERROR, ['bad arguments'])
                                filename = ''
                                file_size = 0
                                isUpload = False
                            except ConnectionError as e:
                                print(f'{username} caused {e} when retry to upload {filename}') 
                            except Exception as e:
                                print(f'{username} caused {e} when retry to upload {filename}') 
                        else:
                            try:
                                send_response(conn, ResponseCodes.UNFINISHED_DOWN, [filename, str(os.path.getsize('server_files/' + filename)), str(64 * 1024)])
                                code, args = recv_command(conn)
                                proccesed_bytes = int(args[0])

                                send_file(conn, 'server_files/' + filename, file_size, proccesed_bytes)

                                filename = ''
                                file_size = 0
                            except (FileNotFoundError, FileExistsError) as e:
                                print(f'{username} caused {e} when retry to download {filename}')
                                send_response(conn, ResponseCodes.ERROR, [filename, 'dont exsist'])
                                filename = ''
                                file_size = 0
                            except (ValueError, IndexError) as e:
                                print(f'{username} caused {e} when retry to download {filename}')
                                send_response(conn, ResponseCodes.ERROR, ['bad arguments'])
                                filename = ''
                                file_size = 0
                            except ConnectionError as e:
                                print(f'{username} caused {e} when retry to download {filename}') 
                            except Exception as e:
                                print(f'{username} caused {e} when retry to download {filename}') 
                    else:
                        try:
                            username = args[0]
                            file_size = 0
                            filename = ''
                            send_response(conn, ResponseCodes.SUCCESS, []) 
                        except IndexError as e:
                            print(f'{username} caused {e} when retry to download {filename}')
                            send_response(conn, ResponseCodes.ERROR, ['bad arguments'])
                            file_size = 0
                            filename = ''


                if command == Commands.ECHO.value:
                    try:
                        print(f'ECHO from {username}: {args[0]}')
                        send_response(conn, ResponseCodes.SUCCESS, [args[0]])
                    except IndexError as e:
                        print(f'{username} caused {e} when retry to download {filename}')
                        send_response(conn, ResponseCodes.ERROR, ['bad arguments'])

                if command == Commands.TIME.value:
                    print(f'TIME from {username}')
                    now = datetime.now().time()
                    send_response(conn, ResponseCodes.SUCCESS, [str(now.hour), str(now.minute), str(now.second)])
                    
                if command == Commands.QUIT.value:
                    print(f'QUIT from {username}')
                    send_response(conn, ResponseCodes.SUCCESS, [])
                    break

                if command == Commands.LIST.value:
                    print(f'LIST from {username}')
                    files = []
                    for file in os.listdir('server_files/'):
                        files.append(file)
                    send_response(conn, ResponseCodes.SUCCESS, files)

                if command == Commands.DOWNLOAD.value:
                    try:
                        filename = args[0]
                        file_size = os.path.getsize('server_files/' + filename) #####################################################################################

                        print(f'DOWNLOAD {filename} from {username}')

                        send_response(conn, ResponseCodes.SUCCESS, [str(file_size), str(64 * 1024)])
                        send_file(conn, 'server_files/' + filename, file_size)
                        filename = ''
                        file_size = 0
                    except (FileNotFoundError, FileExistsError) as e:
                        print(f'{username} caused {e} when try to download {filename}')
                        send_response(conn, ResponseCodes.ERROR, [filename, 'dont exsist'])
                        filename = ''
                        file_size = 0
                    except (ValueError, IndexError) as e:
                        print(f'{username} caused {e} when try to download {filename}')
                        send_response(conn, ResponseCodes.ERROR, ['bad arguments'])
                        filename = ''
                        file_size = 0
                    except ConnectionError as e:
                        print(f'{username} caused {e} when try to download {filename}') 
                    except Exception as e:
                        print(f'{username} caused {e} when try to download {filename}') 

                if command == Commands.UPLOAD.value:
                    try:
                        filename = args[0]
                        file_size = int(args[1])
                        isUpload = True

                        print(f'UPLOAD {filename} from {username}')
                        
                        send_response(conn, ResponseCodes.SUCCESS, [])
                        recv_file(conn, 'server_files/' + filename, file_size)
                        filename = ''
                        file_size = 0
                        isUpload = False
                    except (FileNotFoundError, FileExistsError) as e:
                        print(f'{username} caused {e} when try to upload {filename}')
                        send_response(conn, ResponseCodes.ERROR, [filename, 'dont exsist'])
                        filename = ''
                        file_size = 0
                        isUpload = False
                    except (ValueError, IndexError) as e:
                        print(f'{username} caused {e} when try to upload {filename}')
                        send_response(conn, ResponseCodes.ERROR, ['bad arguments'])
                        filename = ''
                        file_size = 0
                        isUpload = False
                    except ConnectionError as e:
                        print(f'{username} caused {e} when try to upload {filename}') 
                    except Exception as e:
                        print(f'{username} caused {e} when try to upload {filename}') 