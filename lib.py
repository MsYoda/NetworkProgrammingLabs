import math
from random import randint
import socket
import struct

header_format = "I I I"

AN = 0
SN = 0
W = 3

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

def send_large(s: socket, addr, data, segment_size):
    global SN
    global AN
    global W
    data_segments = math.ceil(len(data) // segment_size)
    sended_segmnets = 0

    segments_SNs = []#[SN + i * segment_size for i in range(W)]
    s.settimeout(1)
    while True:
        try:
            for i in range(len(segments_SNs), W):
                segments_SNs.append(SN + i * segment_size)

            for i in range(len(segments_SNs)):
                segment = data[(sended_segmnets + i) * segment_size : (sended_segmnets + i) * segment_size + segment_size]
                s.sendto(struct.pack(header_format, AN, SN + i * len(segment), len(segment)) + segment, addr)

            while True:
                packet, rAddr = s.recvfrom(4096)
                rAn, rSn, length  = struct.unpack(header_format, packet[:4*3])
                
                if rAn <= SN:
                    print(f"In send old packet skiped {SN}")
                    continue
                break

            segments_SNs = [x for x in segments_SNs if x >= rAn]
            sended_segmnets += W - len(segments_SNs)
            SN += (W - len(segments_SNs)) * segment_size

            if (sended_segmnets >= data_segments): break
            
        except socket.timeout:
            print("Dont get ACK")


def recv_large(s: socket, segment_size, data_length):
    global SN
    global AN
    global W

    s.settimeout(1)

    data_segments = math.ceil(data_length / segment_size)
    recv_segments = 0

    data = bytes()

    recv_buf = []

    while True:
        while len(recv_buf) < W:
            try:
                packet, address = s.recvfrom(segment_size + 128) # AN SN LEN
                rAn, rSn, length  = struct.unpack(header_format, packet[:4*3])
                
                if rSn < AN or length == 0:
                    continue

                recv_buf.append((rSn,  packet[4*3:4*3+length]))
                #AN = AN + len(packet[4*3:4*3+length])
            except socket.timeout:
                break

        recv_buf = sorted(recv_buf, key=lambda x: x[0])

        localAN = AN
        for seg in recv_buf:
            if seg[0] != localAN: break
            localAN += segment_size
            data += seg[1]
            recv_segments += 1
        
        AN = localAN

        prob = randint(0, 9)

        if True:
            s.sendto(struct.pack(header_format, AN, SN, 0), address)
        else:
            print("ACK losted")
        
        if recv_segments >= data_segments: break

        recv_buf.clear()
        print(f'recv: AN={AN} SN={SN}')

    s.settimeout(None)
    return data


