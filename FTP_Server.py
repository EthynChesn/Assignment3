from socket import *
from threading import *

serverSocket = socket(AF_INET, SOCK_STREAM)

clients = []
filestorage = {}

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
            file = filestorage[filename]
            print(addr[0] + ' requested ' + filename)
            clientSocket.send(file.encode())
        if IncomingCommand == 'list':
            storagelength = str(len(filestorage))
            clientSocket.send(storagelength.encode())
            for file in filestorage:
                clientSocket.send(file.encode())
                



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