import socket
import os
import json
import hashlib
import re
import time
import datetime
import random
port =12346
server=socket.socket()
server1=socket.socket()
host=socket.gethostname()
try:
    server.bind((host,port))
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
except:
    print 'Error in Server hosting'
    exit(0)
server.listen(5)

def Index(command):
    pattern=''
    if len(command.split())==1:
        client.send("Error in command")
        return
    if len(command.split())==2 and command.split()[1]!='longlist':
        client.send("Error in command")
        return
    if len(command.split())==3 and command.split()[1]!='regex':
        client.send("Error in command")
        return
    if command.split()[1]=='shortlist':
         print  len(command.split())
         if len(command.split())!=6:
            client.send("Error in command")
            return
    if command.split()[1]=='regex':
        pattern=command.split()[2]
    if command.split()[1]=='shortlist':
        start_time=command.split()[2]+' '+command.split()[3]
        start_time=start_time.split('.')[0]
        start_time=time.strptime(start_time,'%Y-%m-%d %H:%M:%S')
        end_time=command.split()[4]+' '+command.split()[5]
        end_time=end_time.split('.')[0]
        end_time=time.strptime(end_time,'%Y-%m-%d %H:%M:%S')
    list_of_files=[]
    try:
        # list_of_files=os.listdir('.')
        for path, subdirs, files in os.walk('.'):
           for filename in files:
             f = os.path.join(path, filename)
             list_of_files.append(f)
    except:
        print "Error in listing the Files in the given Directory"
        client.send("Error")
        return
    for file_name in list_of_files:
        if command.split()[1]=='regex':
            if not re.search(pattern, file_name):
                continue
        try:
            file_stats=os.stat(file_name)
            if command.split()[1]=='shortlist':
                file_mtime=file_stats.st_mtime
                file_mtime=datetime.datetime.fromtimestamp(file_mtime)
                file_mtime=str(file_mtime).split('.')[0]
                file_mtime=time.strptime(file_mtime,'%Y-%m-%d %H:%M:%S')
                if file_mtime<start_time or file_mtime>end_time:
                    continue
            file_info={'file_name':file_name,
                        'file_size':file_stats.st_size,
                        'file_timestamp':file_stats.st_mtime,
                        'file_mode':file_stats.st_mode}
            client.send(json.dumps(file_info))
            x=client.recv(1024)
            if x!='received':
                print "Client received information wrongly"
                client.send("Close the connection")
                break
        except:
            print "Error in finding stats of the file"
    client.send("done!")

def Hash_verify(command):
    hash_md5 = hashlib.md5()
    file_name=command.split()[2]
    try:
        with open(file_name, "rb") as f:
            for data in iter(lambda: f.read(4096), b""):
                hash_md5.update(data)
        f.close()
        return hash_md5.hexdigest()
    except:
        print "Error in file Name"
        return 0;

def Hash_checkall(command):
    list_of_files=[]
    try:
        # list_of_files=os.listdir('.')
        for path, subdirs, files in os.walk('.'):
           for filename in files:
             f = os.path.join(path, filename)
             list_of_files.append(f)
    except:
        print "Error in listing the Files in the given Directory"
        print "Error"
        return
    for file_name in list_of_files:
        try:
            cmd='hash verify '+str(file_name)
            stats=os.stat(file_name)
            info={'file_name':file_name,'hash':Hash_verify(cmd),
                    'mode':stats.st_mode,'time_stamp':stats.st_mtime}
            client.send(json.dumps(info))
            if client.recv(1024)!='received':
                break
        except:
            print "Error in finding stats of the file"
    client.send("done!")

def send_file_TCP(command):
    file_name=command.split()[2]
    try:
        File = open(file_name,'rb')
        client.send('File Exists')
        if client.recv(1024)!='Execute':
            return
        data = File.read(1024)
        while (data):
            client.send(data)
            if client.recv(1024)!='received':
                break
            data = File.read(1024)
        File.close()
        client.send('Done Sending')
        print "Done Sending!!!!!!!!!!!"
    except:
        client.send("Error in File opening")
        print "Error in File opening"
def createport(server1):
    PORT1=random.randint(5000, 6000)
    try:
        server1.bind((host,PORT1))
        server1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except:
        return createport(server1)
    return PORT1

def send_file_UDP(command):
    server1=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.send(str(createport(server1)))
    data1,addr1 =server1.recvfrom(1024)
    if data1!='received':
        return
    file_name=command.split()[2]
    try:
        File = open(file_name,'rb')
        server1.sendto('File Exists',addr1)
        data1,addr1=server1.recvfrom(1024)
        if data1!='Execute':
            return
        data = File.read(1024)
        while (data):
            server1.sendto(data,addr1)
            data1,addr1=server1.recvfrom(1024)
            if data1!='received':
                break
            data = File.read(1024)
        File.close()
        server1.sendto('Done Sending',addr1)
        print "Done Sending!!!!!!!!!!!"
    except:
        server1.sendto("Error in File opening",addr1)
        print "Error in File opening"
    server1.close()

if __name__=="__main__":
    while True:
        try:
            client,address=server.accept()
        except:
            print "Server Closed"
            server.close()
            break
        while True:
            try:
                command=client.recv(1024)
            except:
                print "Connection closed"
                break
            if not len(command.split()):
                client.close()
                print "Connection closed"
                break
            if command.split()[0]=='index':
                Index(command)
            elif command.split()[0]=='hash':
                if len(command.split())==3 and command.split()[1]=='verify':
                    stats=os.stat(command.split()[2])
                    info={'file_name':command.split()[2],
                            'hash':Hash_verify(command),'mode':stats.st_mode,'time_stamp':stats.st_mtime}
                    client.send(json.dumps(info))
                elif command.split()[1]=='checkall':
                    Hash_checkall(command)
                else:
                    client.send("Error in command")
            elif command.split()[0]=='download':
                if len(command.split())!=3:
                    client.send("Error in commad")
                if command.split()[1]=='TCP':
                    send_file_TCP(command)
                if command.split()[1]=='UDP':
                    send_file_UDP(command)
            else:
                client.send("Error in command")
    server.close()
