from socket import *
from threading import *
import sys

def put(filename):
    file = open(filename,'r')
    file = filename + ':' + file.read()
    clientSocket.send(file.encode())

def InputListener():
    Message = input()
    if Message.startswith('put '):
        put(Message.removeprefix('put '))



hostname = gethostname()
IPAddr = gethostbyname(hostname)
Server = '10.200.20.108'
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
