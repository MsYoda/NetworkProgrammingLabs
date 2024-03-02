from random import randint
import socket
import struct

header_format = "I I I"

AN = 0
SN = 0


def recv(s: socket):
    global AN
    global SN
    while True:
        packet, address = s.recvfrom(4096) # AN SN LEN
        rAn, rSn, length  = struct.unpack(header_format, packet[:4*3])

        if rSn < AN or length == 0:
            continue

        data = packet[4*3:4*3+length]

        AN = AN + len(data)
        prob = randint(0, 9)

        if prob > 6:
            s.sendto(struct.pack(header_format, AN, SN, 0), address)
        else:
            print("ACK losted")
        
        print(f'recv: AN={AN} SN={SN}')
        return data, address
    
def send(s: socket, addr, data):
    global SN
    global AN
    s.settimeout(0.5)
    while True:
        try:
            s.sendto(struct.pack(header_format, AN, SN, len(data)) + data, addr)
            packet, rAddr = s.recvfrom(4096)
            rAn, rSn, length  = struct.unpack(header_format, packet[:4*3])
            if rAn <= SN:
                print("In send old packet skiped")
                continue

            SN = SN + len(data)
            break
        except socket.timeout:
            print("Dont get ACK")
    s.settimeout(None)
    print(f'send: AN={AN} SN={SN}')
    
