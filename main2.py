import sys
import socket
import re
import os
import struct
import socket
import time
import sys

from dnslib import *
from ping import verbose_ping


#--------------reading config ------------------
class Config:
    name = ""
    dest = ""
    protocol = ""
    port = 0
    send_pattern = ""
    response = ""
    interval = 0
    last_check = 0

    def parse(self,str):
        arr = str.split(',')
        self.name = arr[0]
        self.dest = arr[1]
        self.protocol = arr[2]
        if len(arr[3])>0:
            self.port = int(arr[3])
        self.send_pattern = arr[4]
        self.send_pattern = self.send_pattern.replace("\\r","\r");
        self.send_pattern = self.send_pattern.replace("\\n","\n");

        self.response = arr[5]
        self.interval = int(arr[6])

def load_config(path):
    configs = []
    filepath = path
    with open(filepath) as fp:
        line = fp.readline()
        while line:
            line = fp.readline()
            line = line.strip();
            if len(line)>5 and line.startswith('#') == 0:
                c = Config()
                c.parse(line)
                configs.append(c)
    return configs

def tcp_check_response(dest,port,content,response_contains):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.connect((dest, port))
        s.send(str.encode(content))
        data = (s.recv(1000000))
        s.shutdown(1)
        s.close()
        print('Received', repr(data))
        if data.find(str.encode(response_contains))==-1:
            return False
        else:
            return True
    except:
        return False
def tcp_check_connect(dest,port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.30)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.connect((dest, port))
        return True
    except:
        return False
def dns_check(server,port,address):
    try:
        d = DNSRecord.question(address);
        # Sending the packet
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', 8888))
        sock.settimeout(2)
        sock.sendto(d.pack(), (server, port))
        #print("Packet Sent")
        data, addr = sock.recvfrom(1024)
        sock.close()
        d =  DNSRecord.parse(data);
        res = repr(d);
        #print(d)
        if res.find("RR: '"+address+".'")==-1:
            return False;
        else:
            return True;
    except:
        return False;
def icmp_check(server):
    s = verbose_ping(server, 1000, 1,8)
    if not s:
        return False;
    if s.fracLoss==0:
        return True
    else:
        return False

def check(config):
    if config.protocol == 'ICMP':
        return icmp_check(config.dest)
    if config.protocol == 'DNS':
        return dns_check(config.dest,config.port,config.send_pattern)
    if config.protocol=="TCP":
        if len(config.send_pattern)>0 and len(config.response)>0:
            return tcp_check_response(config.dest,config.port,config.send_pattern,config.response)
        else:
            return tcp_check_connect(config.dest,config.port)






#------------------------------------------



#print(dns_check("8.8.8.8","53","google.com"))

#rep = tcp_check_response("honar8.com",80,"GET / HTTP/1.0\r\n\r\n","200 OK")
#print(rep)

#verbose_ping("honar8.com", 1000, 1,8)
#print(icmp_check("honar8.com"))


#rep = tcp_check_connect("imap.gmail.com",993)
#print(rep)

#rep = tcp_check_connect("54.36.26.51",33096)
#print(rep)



print('using python version:' + sys.version)
configs = load_config('config2.txt');


#for c in configs:
    #print(c.name,c.interval)

while 1:
    print('running...')
    tt = time.time();
    for c in configs:
        if c.last_check+c.interval<tt:
            print('checking ' + c.name)
            c.last_check = tt
            res = check(c)
            f = open('results2.txt', 'a')
            f.write(c.name+","+str(res)+","+str(int(time.time()))+"\n")
            f.close()
    time.sleep(1)
