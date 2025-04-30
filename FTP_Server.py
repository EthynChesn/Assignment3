from socket import *
from threading import *
import time

serverSocket = socket(AF_INET, SOCK_STREAM)

clients = []
filestorage = {}

def WaitNext(clientSocket):
    if clientSocket.recv(1024).decode() == 'True':
        return

def NewClient(clientSocket, addr):
    global clients
    clients += (clientSocket, addr[1])
    while True:
        IncomingCommand = clientSocket.recv(1024).decode()
        if IncomingCommand == 'put':
            filename = clientSocket.recv(1024).decode()
            filecontent = clientSocket.recv(1024).decode()
            filestorage[filename] = filecontent
            print(addr[0] + " Uploaded " + filename)
        if IncomingCommand == 'get':
            filename = clientSocket.recv(1024).decode()
            print(addr[0] + ' requested ' + filename)
            if not filename in filestorage:
                print(addr[0] + ' Problem: ' + filename + " Not Found" )
                clientSocket.send('error'.encode())
            else:
                file = filestorage[filename]
                clientSocket.send(file.encode())
        if IncomingCommand == 'list':
            storagelength = str(len(filestorage))  
            clientSocket.send(storagelength.encode())
            if len(filestorage) > 0:
                Acknowledge = clientSocket.recv(1024).decode()
                if Acknowledge == 'True':
                    for file in filestorage:
                        clientSocket.send(file.encode())
                        WaitNext(clientSocket)
                Acknowledge = False
        if IncomingCommand == 'delete':
            clientSocket.send('True'.encode())
            filename = clientSocket.recv(1024).decode()
            print(addr[0] + ' is attempting to delete ' + filename)
            if filename in filestorage:
                del filestorage[filename]
                clientSocket.send('deleted'.encode())
                print(filename + ' deleted by ' + addr[0])
            else:
                clientSocket.send('error'.encode())
                print(addr[0] + ' Problem: ' + filename + ' Not Found')
        if IncomingCommand == 'close':
            clientSocket.send('True'.encode())
            clientSocket.close()
            print(addr[0] + ' has disconnected')
            break


def main():
    Host = '0.0.0.0'
    Port = 12345

    serverSocket.bind((Host, Port))
    serverSocket.listen(5)
    print('Listening for clients to connect...')
    serverMessage = 'Welcome!'

    while True:
        Connection, addr = serverSocket.accept()
        print('Got connection: ' + str(addr))
        print('Listening for clients to connect...')
        ClientThread = Thread(target=NewClient, args=(Connection,addr))
        ClientThread.start()
        Connection.send(serverMessage.encode())

if __name__ == '__main__':
    main()