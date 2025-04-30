from socket import *
from threading import *
import sys

def put(filename):
    clientSocket.send('put'.encode())
    file = open(filename,'r')
    Char = filename[-1]
    Counter = -1
    while not Char == "\\":
        Counter -= 1
        Char = filename[Counter]
    shortname = ''
    for index in range(Counter+1,-1):
        shortname += filename[index]
    shortname += filename[-1]
    file = file.read()
    clientSocket.send(shortname.encode())
    clientSocket.send(file.encode())
    print('Succesfully Uploaded ' + filename)

def get(getfilename):
    global filePath
    Request = getfilename
    clientSocket.send('get'.encode())
    clientSocket.send(Request.encode())
    filecontent = clientSocket.recv(1024).decode()
    with open(filePath+getfilename, 'w') as Writefile:
        Writefile.write(filecontent)
    print(getfilename + " Downloaded succesfully")

def InputListener():
    Message = input()
    if Message.startswith('put '):
        put(Message.removeprefix('put '))
    elif Message.startswith('get '):
        get(Message.removeprefix('get '))
    elif Message == 'list':
        clientSocket.send('list'.encode())
        listlength = clientSocket.recv(1024).decode()
        if not listlength[0].isdigit():
            listlength = clientSocket.recv(1024).decode()
        if len(listlength) > 2:
            listlength = listlength[0:2]
            if not listlength[1].isdigit():
                listlength = listlength[0]

            listlength = clientSocket.recv(1024).decode()     
        listlength = int(listlength)
        print('List of Files on the Server:')
        for filelist in range(listlength):
            file = clientSocket.recv(1024).decode()
            print(file)


filePath = "YOURPATH (RECOMMEND ROOT OF DRIVE)"
hostname = gethostname()
IPAddr = gethostbyname(hostname)
Server = 'HOSTIP (IP of DEVICE HOSTING SERVER)'
Port = 12345

#Create socket
clientSocket = socket(AF_INET, SOCK_STREAM)

#Connect client to server
clientSocket.connect((Server, Port))

#Receive and print initial information
print(clientSocket.recv(1024).decode())

while True:
    InputThread = Thread(target=InputListener)
    InputThread.start()
