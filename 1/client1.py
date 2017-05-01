import socket
import os
import sys
import json
import hashlib
import time
import datetime
port =12346
client=socket.socket()
host=socket.gethostname()
try:
    client.connect((host,port));
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
except:
    print 'Error in client connection with server'
    exit(0)

def Index(command):
    client.send(command)
    file_info = client.recv(1024)
    if file_info=='Error in command':
        print "Please check the command"
        return
    if file_info=='Error':
        print 'Error'
        return
    while file_info!='done!':
        file_info=json.loads(file_info)
        print file_info['file_timestamp']
        time_stamp=datetime.datetime.fromtimestamp(file_info['file_timestamp'])
        print str(file_info['file_name'])+'\t'+str(file_info['file_size'])+'\t'+str(time_stamp)+'\t'+'file'
        client.send("received")
        file_info=client.recv(1024)
        if file_info=='Close the connection':
            break

def download_file_TCP(command):
    client.send(command)
    info=client.recv(1024)
    if info=='Error in command':
        print "Please check the command"
        return
    if info!='File Exists':
        print "Error in File Opening"
        return
    client.send('Execute')
    file_name=command.split()[2]
    if len(file_name.split('/'))!=1:
        if not os.path.exists(os.path.dirname(file_name)):
            os.makedirs(os.path.dirname(file_name))
    with open(file_name, 'wb') as f:
        while True:
            data = client.recv(1024)
            if data=='Done Sending':
                break
            client.send('received')
            f.write(data)
    f.close()
    orginal_info=Hash_verify('hash verify '+str(command.split()[2]))
    orginal_hash=orginal_info['hash']
    orginal_mode=orginal_info['mode']
    downloaded_hash=str(Compute_hash(command.split()[2]))
    if downloaded_hash==orginal_hash:
        os.chmod(command.split()[2],give_permissions(orginal_mode))
        print 'Download Successful'
    else:
        print 'Download Unsuccessful'

def download_file_UDP(command):
    client.send(command)
    port1=int(client.recv(1024))
    client1=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    addr=(host,port1)
    client1.sendto('received',addr)
    info,addr=client1.recvfrom(1024)
    if info=='Error in command':
        print "Please check the command"
        return
    if info!='File Exists':
        print "Error in File Opening"
        return
    client1.sendto('Execute',addr)
    file_name=command.split()[2]
    if len(file_name.split('/'))!=1:
        if not os.path.exists(os.path.dirname(file_name)):
            os.makedirs(os.path.dirname(file_name))
    with open(file_name, 'wb') as f:
        while True:
            data,addr = client1.recvfrom(1024)
            if data=='Done Sending':
                break
            client1.sendto('received',addr)
            f.write(data)
    f.close()
    client1.close()
    orginal_info=Hash_verify('hash verify '+str(command.split()[2]))
    orginal_hash=orginal_info['hash']
    orginal_mode=orginal_info['mode']
    downloaded_hash=str(Compute_hash(command.split()[2]))
    if downloaded_hash==orginal_hash:
        os.chmod(command.split()[2],give_permissions(orginal_mode))
        print 'Download Successful'
    else:
        print 'Download Unsuccessful'

def give_permissions(orginal_mode):
    x=0
    c=orginal_mode
    mode=''
    while c>0:
        mode+=str(c%2)
        c=c/2
    permissions=''
    while x<3:
        permissions=str(int(mode[3*x+0])+2*int(mode[3*x+1])+4*int(mode[3*x+2]))+permissions
        x=x+1
    permissions=int(permissions,8)
    return permissions

def Hash_verify(command):
    client.send(command)
    return json.loads(client.recv(1024))

def Compute_hash(file_name):
    hash_md5 = hashlib.md5()
    try:
        with open(file_name, "rb") as f:
            for data in iter(lambda: f.read(4096), b""):
                hash_md5.update(data)
        f.close()
        return hash_md5.hexdigest()
    except:
        return 0;


def Hash_checkall(command):
    client.send(command)
    print command
    info=client.recv(1024)
    list_of_files=[]
    if info=="Error in command":
        print "please check the command"
    while info!='done!':
        # print info
        list_of_files.append(json.loads(info))
        client.send("received")
        info=client.recv(1024)
    return list_of_files

def Automate():
    total_info=Hash_checkall('hash checkall')
    for file_info in total_info:
        shared_File_hash=file_info['hash']
        present_File_hash=Compute_hash(file_info['file_name'])
        if present_File_hash==0:
            print file_info['file_name']
            download_file_TCP('download TCP '+file_info['file_name'])
        elif shared_File_hash!=present_File_hash:
            shared_File_mtime=datetime.datetime.fromtimestamp(file_info['time_stamp'])
            shared_File_mtime=str(shared_File_mtime).split('.')[0]
            print shared_File_mtime
            shared_File_mtime=time.strptime(shared_File_mtime,'%Y-%m-%d %H:%M:%S')
            file_stats=os.stat(file_info['file_name'])
            present_File_mtime=datetime.datetime.fromtimestamp(file_stats.st_mtime)
            present_File_mtime=str(present_File_mtime).split('.')[0]
            print present_File_mtime
            present_File_mtime=time.strptime(present_File_mtime,'%Y-%m-%d %H:%M:%S')
            if shared_File_mtime>present_File_mtime:
                print file_info['file_name']
                download_file_TCP('download TCP '+file_info['file_name'])



if __name__=="__main__":
    prompt=0
    gap=time.strptime('0:00:01','%H:%M:%S')
    past_time=datetime.datetime.now()
    prompt=0
    automate=0
    if len(sys.argv)!=2:
        print "prompt or automate as argument"
        exit(0)
    if sys.argv[1]=='prompt':
        prompt=1
    elif sys.argv[1]=='automate':
        automate=1
    else:
        print "prompt or automate"
        exit(0)
    while prompt:
        command=raw_input('prompt>')
        if command==1:
            break
        if command=='':
            continue
        if command=='close':
            client.close()
            break
        elif command.split()[0]=='index':
                Index(command)
        elif command.split()[0]=='hash':
            if command.split()[1]=='verify':
                file_info=Hash_verify(command)
                time_stamp=datetime.datetime.fromtimestamp(file_info['time_stamp'])
                print str(file_info['file_name'])+'\t'+str(file_info['hash'])+'\t'+str(time_stamp)
            elif command.split()[1]=='checkall':
                list_of_files=Hash_checkall(command)
                for file_info in list_of_files:
                    time_stamp=datetime.datetime.fromtimestamp(file_info['time_stamp'])
                    print str(file_info['file_name'])+'\t'+str(file_info['hash'])+'\t'+str(time_stamp)
        elif command.split()[0]=='download':
            if len(command.split())!=3:
                print "Please check the command"
            if command.split()[1]=='TCP':
                download_file_TCP(command)
            if command.split()[1]=='UDP':
                download_file_UDP(command)
        else:
            print "Please check the command"
    #client.close()
    while automate:
        current_time=datetime.datetime.now()
        diff=time.strptime(str(current_time-past_time).split('.')[0],'%H:%M:%S')
        if diff > gap:
            print current_time
            Automate()
            past_time=current_time
