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
DATA_PACKET = 0
################################################################################


def main():
    #checking if all ports entered are integers
    try:
        r_in_port = int(sys.argv[1])
        r_out_port = int(sys.argv[2])
        cr_in_port = int(sys.argv[3])
        file_name = sys.argv[4]
    except:
        print("Please use only integers for port numbers")
    #checking if the port numbers and packet loss are within the defined boundries
    if len({r_in_port, r_out_port, cr_in_port}) != 3:
        print("port numbers are to be distinct")
    if min_port >= r_in_port >= max_port or min_port >= r_out_port >= max_port:
        print("port numbers must be within 1024 and 64000")
    
    #Creating sockets and binding the ports
    r_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    r_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    host = "127.0.0.1"
    try:
        r_in.bind((host, r_in_port))
        r_out.bind((host, r_out_port))
    except:
        print("ERROR: PORT ERROR")
        r_in.close()
        r_out.close()
    r_out.connect((host, cr_in_port))

    if os.path.isfile(file_name):
        print("File", file_name, "File already exists. Please change new file name")
        r_in.close()
        r_out.close()

    fk = open(file_name, 'wb')
    through = 0
    while True:
        readable, _, _ = select.select([r_in], [], [], 1)
        if r_in in readable:
            packet = r_in.recv(max_buffer)
            magicno, typ, seqno, datalen, body = packet_bytes(packet)
            if typ != DATA_PACKET or magicno != magic_number:
                continue
            if seqno != through:
                packet_transport = Packet(magic_number, acknowledgement_packet, seqno, 0,
                        None)
                packet_transport = packet_transport.converting_string_byte()
                try:
                    r_out.send(packet_transport)
                except:
                    print("ERROR: RECEIVER ERROR")
                    fk.close()
                    r_in.close()
                    r_out.close()
                continue
            else:
                packet_transport = Packet(magic_number, acknowledgement_packet, seqno, 0,
                            None)
                packet_transport = packet_transport.converting_string_byte()
                try:
                    r_out.send(packet_transport)
                except:
                    print("ERROR: RECEIVER ERROR")
                    fk.close()
                    r_in.close()
                    r_out.close()
                through = 1 - through
                fk.write(body)
            if datalen == 0:
                print("Success, the file was written to!!!")
                fk.close()
                r_in.close()
                r_out.close()
                return 0

if __name__ == "__main__":
    main()
