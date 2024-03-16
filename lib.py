import math
from random import randint
import socket
import struct

header_format = "I I I"
header = "I I"

AN = 0
SN = 0
W = 20

def recv(s: socket):
    global AN
    global SN
    while True:
        packet, address = s.recvfrom(256*1024) # AN SN LEN
        rAn, rSn, length  = struct.unpack(header_format, packet[:4*3])

        if rSn < AN or length == 0:
            continue

        data = packet[4*3:4*3+length]

        AN = AN + 1
        prob = randint(0, 9)

        if True:
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
            while True:
                packet, rAddr = s.recvfrom(256*1024)
                rAn, rSn, length  = struct.unpack(header_format, packet[:4*3])
                if rAn <= SN:
                    #print("In send old packet skiped")
                    continue
                else: break

            SN = SN + 1
            break
        except socket.timeout:
            print("Dont get ACK")
    s.settimeout(None)
    print(f'send: AN={AN} SN={SN}')

def send_large(s: socket, addr, data, segment_size = 64500):
    data_segments = math.ceil(len(data) / segment_size)
    not_sended_segmnets = list(range(0, data_segments))

    data = [data[i:i+segment_size] for i in range(0, len(data), segment_size)]

    while True:
        counter = 0
        for i in not_sended_segmnets:
            s.sendto(struct.pack(header_format, i, 0, len(data[i])) + data[i], addr)
            counter += 1
            if counter > 750: break

        r_data, addr = s.recvfrom(segment_size)
        r_data = r_data[3:]
        int_chunks = [r_data[i:i+4] for i in range(0, len(r_data), 4)]
        not_sended_segmnets = [int.from_bytes(chunk, byteorder='big') for chunk in int_chunks]
       # print(f'Not sended segmnets: {not_sended_segmnets}')
        if len(not_sended_segmnets) == 0: break
       



def recv_large(s: socket, data_length, addr, segment_size = 64500):
    recv_segmnets = []
    not_recv_segmnets = []

    data = bytes()
    data_segments = math.ceil(data_length / segment_size)

    expected_segments = list(range(0, data_segments))

    s.settimeout(0.00001)
    while True:
        try:
            segmnet, addr = s.recvfrom(segment_size + 4*3)
            #print('recvfrom')
            sn, r, length = struct.unpack(header_format, segmnet[:4*3])
            recv_segmnets.append((sn, segmnet[4*3:]))
            
        except socket.timeout:
            recv_segmnets = sorted(recv_segmnets, key=lambda x: x[0])

            actual_segments = [item[0] for item in recv_segmnets]
            not_recv_segmnets = set(expected_segments) - set(actual_segments)

            s.sendto(b'ACK' + b''.join(x.to_bytes(4, 'big') for x in not_recv_segmnets), addr)

            if len(not_recv_segmnets) == 0: break

    s.settimeout(None)
    for segment in recv_segmnets:
        data += segment[1]
    return data


