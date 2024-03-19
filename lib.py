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

        try:
            rAn, rSn, length  = struct.unpack(header_format, packet[:4*3])
        except struct.error:
            continue

        if rSn < AN or length == 0:
            s.sendto(struct.pack(header_format, AN, SN, 0), address)
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

def send_large(s: socket, addr, data, segment_size = 65000):
    global SN
    data_segments = math.ceil(len(data) / segment_size)
    not_sended_segmnets = list(range(0, data_segments))

    #data = [data[i:i+segment_size] for i in range(0, len(data), segment_size)]

    while True:
        for i in not_sended_segmnets:
            segment = data[i * segment_size : i * segment_size + segment_size]
            s.sendto(struct.pack(header_format, AN, SN, i) + segment, addr)

        r_data, addr = s.recvfrom(segment_size)
        rAN = r_data[:4]
        rAn = int.from_bytes(rAN, byteorder = 'big')
       # print(f'RECV AN: {rAn} | CUR SN {SN}')
        if (int.from_bytes(rAN, byteorder = 'big') > SN):
           break
        r_data = r_data[4:]
        int_chunks = [r_data[i:i+4] for i in range(0, len(r_data), 4)]
        not_sended_segmnets = [int.from_bytes(chunk, byteorder='big') for chunk in int_chunks]
       # print(f'Not sended segmnets: {not_sended_segmnets}')
        if len(not_sended_segmnets) == 0: break

    print('END SEND')
    SN += 1
       



def recv_large(s: socket, data_length, addr, segment_size = 65000):
    global AN
    recv_segmnets = {}
    not_recv_segmnets = []

    data = bytes()
    data_segments = math.ceil(data_length / segment_size)

    expected_segments = list(range(0, data_segments))
    not_recv_segmnets = expected_segments

    timeout = 0.2

    recv_segmnets_len = 0
    s.settimeout(0.2)
    while True:
        try:
            segmnet, addr = s.recvfrom(segment_size + 4*3)
            an, rSN, sn = struct.unpack(header_format, segmnet[:4*3])
            if rSN < AN:
                #print("Skip segments")
                continue

            timeout -= 0.002
            if timeout < 0.12: timeout = 0.12

            recv_segmnets[sn] = segmnet[4*3:]
            
        except socket.timeout:
            timeout += 0.08
            if timeout > 0.28: timeout = 0.28

            if (len(recv_segmnets) > recv_segmnets_len):
                recv_segmnets_len = len(recv_segmnets)
                recv_segmnets =  dict(sorted(recv_segmnets.items()))

                actual_segments = [item for item in recv_segmnets.keys()]
                not_recv_segmnets = set(expected_segments) - set(actual_segments)
                #print(f'actual_segments {actual_segments}')
                #print(f'not rect segmnets {not_recv_segmnets}')
                #print('Send not_recv_segmnets to server')
            #print(f'Send AN: {AN}')

            
            s.sendto(AN.to_bytes(4, 'big') + b''.join(x.to_bytes(4, 'big') for x in not_recv_segmnets), addr)

            if len(not_recv_segmnets) == 0: break

    s.settimeout(None)
    AN += 1
   # print('ENd sending')
    return b''.join(segment for segment in recv_segmnets.values())

def get_hi():
    global AN 
    global SN
    AN = 0
    SN = 0


