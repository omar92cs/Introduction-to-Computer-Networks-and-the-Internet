"""
COSC264 Assignment
Done by: Ahmad Alsaleh and Aiman Hazashah
"""


import socket
import sys
import os
import select
from channel import Packet
from channel import packet_bytes

################################################################################
acknowledgement_packet = 1
magic_number = 0x497E
min_port = 1024
max_port = 64000
max_buffer = 512
host = '127.0.0.1'
datapacket = 0
################################################################################

def main():
    #checking if all ports entered are integers
    try:
        s_in_port = int(sys.argv[1])
        s_out_port = int(sys.argv[2])
        cs_in_port = int(sys.argv[3])
        file_name = sys.argv[4]
    except:
        print("Please use only integers for port numbers")
    #checking if the port numbers and packet loss are within the defined boundries
    if len({s_in_port, s_out_port, cs_in_port}) != 3:
        print("port numbers are to be distinct")
    if min_port >= s_in_port >= max_port or min_port >= s_out_port >= max_port:
        print("port numbers must be within 1024 and 64000")

    #Creating sockets and binding the ports
    s_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    host = "127.0.0.1"
    
    try:
        s_in.bind((host, s_in_port))
        s_out.bind((host, s_out_port))
    except:
        print("ERROR: SENDER ERROR")
        s_in.close()
        s_out.close()

    s_out.connect((host, cs_in_port))

    if not os.path.isfile(file_name):
        print("File", file_name,  "No such file exists")
        s_in.close()
        s_out.close()

    fp = open(file_name, 'rb')
    seq_num = 0
    exit_flag = False
    counter = 0
    
    while not exit_flag:
        data = fp.read(max_buffer)
        data_len = len(data)
        if data_len == 0:
            buff_packet = Packet(magic_number, datapacket, seq_num, data_len, None)
            p_buff = buff_packet.converting_string_byte()
            exit_flag = True
        else:
            buff_packet = Packet(magic_number, datapacket, seq_num, data_len, data)
            p_buff = buff_packet.converting_string_byte()

        while True:
            try:
                s_out.send(p_buff)
            except:
                print("ERROR: SENDOR ERROR")
                fp.close()
                s_in.close()
                s_out.close()
            counter += 1
            recvd, _, _ = select.select([s_in], [], [], 1)
            if s_in in recvd:
                packet = s_in.recv(max_buffer)
                magicno, my_type, seqno, datalen, body = packet_bytes(packet)
                if my_type != acknowledgement_packet or \
                                    magicno != magic_number or \
                                    datalen != 0:
                    continue
                if seqno == seq_num:
                    seq_num = 1 - seq_num
                    if exit_flag:
                        print("Amount of packets sent are: " + str(counter))
                    break
    fp.close()
    s_in.close()
    s_out.close()

if __name__ == "__main__":
    main()
