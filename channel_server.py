"""
COSC264 Assignment
Done by: Ahmad Alsaleh and Aiman Hazashah
"""


import sys
import select
import socket
import struct
import random
import time

################################################################################
acknowledgement_packet = 1
magic_number = 0x497E
min_port = 1024
max_port = 64000
max_buffer = 512
host = '127.0.0.1'
################################################################################

class Packet():
    def __init__(self, magicno, my_type, seqno, dataLength, data):
        self.magicno = magicno
        self.type = my_type
        self.seqno = seqno
        self.dataLength = dataLength
        self.data = data

    def converting_string_byte(self):
        st = struct.pack('iiii', self.magicno, self.type, self.seqno, self.dataLength)
        #Struct supports packing data into a string, and unpacking data from strings
        if self.data == None:
            packet = st
        else:
            body = self.data
            packet = st + body            
        return packet
    
def packet_bytes(bytes):
    st, body = bytes[:16], bytes[16:]
    magicno, my_type, seqno, dataLength = struct.unpack('iiii', st)
    return [magicno, my_type, seqno, dataLength, body]

def packet_check(packet, packet_loss):
    magicno, my_type, seqno, dataLength, body = packet_bytes(packet)
    u = random.uniform(0, 1)
    if magicno != magic_number or u < packet_loss:
        return "dropped"

    return "success"

def main():
    #checking if all ports entered are integers
    try:
        csin = int(sys.argv[1])
        csout = int(sys.argv[2])
        crin = int(sys.argv[3])
        crout = int(sys.argv[4])
        
        #Port for channel to send packets destined to the sender (using its own socket cs_out)
        sin = int(sys.argv[5])
        
        #port for channel to send packets destined to the receiver (using its own socket cr_out)
        rin = int(sys.argv[6])
        
        print("Confirmed all selected ports are numbers")
    except:
        print("Please use only integers for port numbers")
    
    #checking if the packet loss rate is a float
    try:
        packet_loss = float(sys.argv[7])
    except:
        print("the packet loss rate has to be a number between 0 <= P < 1")    

    #checking if the port numbers and packet loss are within the defined boundries
    if (min_port >= csin >= max_port) or (min_port >= csout >= max_port) or (min_port >=crin >= max_port) or (min_port >= crout >= max_port):
        print("port numbers must be within 1024 and 64000")
    if len({csin, csout, crin, crout, sin, rin}) != 6:
        print("port numbers are to be distinct")
    if (packet_loss < 0) and (packet_loss >= 1):
        print("packet loss must be within 0 <= P < 1")
    
    #Creating sockets and binding the ports
    try:
        sock_csin = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        sock_csin.bind((host, csin))
        print("Socket csin binded")
    except:
        print("Socket csin could not be binded")
        sock_csin.close()
    
    try:
        sock_csout = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        sock_csout.bind((host, csout))
        print("Socket csout binded")
    except:
        print("Socket csout could not be binded")
        sock_csout.close()

    try:
        sock_crin = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        sock_crin.bind((host, crin))
        print("Socket crin binded")
    except:
        print("Socket crin could not be binded")
        sock_crin.close()
        
    
    try:
        sock_crout = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        sock_crout.bind((host, crout))
        print("Socket crout binded")
    except:
        print("Socket crout could not be binded")
        sock_crout.close()
    
    time.sleep(10) #waiting for connections from sender and receiver
    
    #connections created
    sock_csout.connect((host, sin)) 
    sock_crout.connect((host, rin))
    
    #generating a random number
    random.seed()
    
    #looping through infinitly
    while True:
        readable, _, _ = select.select([sock_csin, sock_crin], [], [], 1)
        if sock_csin in readable:
            data1, add1 = sock_csin.recvfrom(max_buffer)
            drop = packet_check(data1, packet_loss)
            if drop == "dropped":
                continue
            else:
                try:
                    sock_crout.send(data1)
                except:
                    print("ERROR: Packet was not sent to receiver.")
                    break;
        if sock_crin in readable:
            data2, add2 = sock_crin.recvfrom(max_buffer)
            drop = packet_check(data2, packet_loss)
            if drop == "dropped":
                continue
            else:
                try:
                    sock_csout.send(data2)
                except:
                    print("ERROR: Packet was not sent to sender.")
                    
    sock_csin.close()
    sock_csout.close()
    sock_crin.close()
    sock_crout.close()


if __name__ == "__main__":
    main()
