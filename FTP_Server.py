from socket import *
from threading import *

serverSocket = socket(AF_INET, SOCK_STREAM)

clients = []
filestorage = {}

def NewClient(clientSocket, addr):
    global clients
    clients += (clientSocket, addr[1])
    while True:
        Incoming = clientSocket.recv(1024).decode()
        Index = 0
        filename = ''
        while not Incoming[Index] == ':':
            filename += Incoming[Index]
            Incoming  = Incoming[Index+1:]
            Index += 1
        filecontent = Incoming
        filestorage[(filename,addr[1])] = filecontent


def main():
    Host = '0.0.0.0'
    Port = 12345

    serverSocket.bind((Host, Port))
    serverSocket.listen(5)

    serverMessage = 'Welcome!'

    while True:
        Connection, addr = serverSocket.accept()
        ClientThread = Thread(target=NewClient, args=(Connection,addr))
        ClientThread.start()
        print('Got Connection', addr)
    
        Connection.send(serverMessage.encode())

if __name__ == '__main__':
    main()