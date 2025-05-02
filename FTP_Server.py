from socket import *
from threading import *
from datetime import datetime
import sys

serverSocket = socket(AF_INET, SOCK_STREAM)

clients = []
filestorage = {}

def WaitNext(clientSocket):
    if clientSocket.recv(1024).decode() == 'True':
        return

def NewClient(clientSocket, addr, username):
    global clients
    while True:
        IncomingCommand = clientSocket.recv(1024).decode()
        if IncomingCommand == 'put':
            filename = clientSocket.recv(1024).decode()
            filecontent = clientSocket.recv(1024).decode()
            filestorage[filename] = filecontent
            print(username + " Uploaded " + filename)
        if IncomingCommand == 'get':
            filename = clientSocket.recv(1024).decode()
            print(username + ' requested ' + filename)
            if not filename in filestorage:
                print(username + ' Problem: ' + filename + " Not Found" )
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
            print(username + ' is attempting to delete ' + filename)
            if filename in filestorage:
                del filestorage[filename]
                clientSocket.send('deleted'.encode())
                print(filename + ' deleted by ' + username)
            else:
                clientSocket.send('error'.encode())
                print(username + ' Problem: ' + filename + ' Not Found')
        if IncomingCommand == 'close':
            clientSocket.send('True'.encode())
            clientSocket.close()
            print(username + ' has disconnected')
            clients.remove(username)
            break

def InputListener():
    filePath = r'E:\\'
    while True:
        Command = input()
        if Command == "listfiles":
            if len(filestorage) > 0:
                print('List of Files on Server:')
                for file in filestorage:
                    print(file)
            else:
                print('Problem: List of Files is Empty')
        elif Command == "listusers":
            if len(clients) > 0:
                print('List of Users Connected to Server:')
                for client in clients:
                    print(client)
            else:
                print('Problem: No Users are Currently Connected')
        elif Command.startswith('delete '):
            filename = Command.removeprefix('delete ')
            if filename in filestorage:
                del filestorage[filename]
                print('deleted ' + filename)
            else:
                print('Problem: File Not Found')
        elif Command == 'backup':
            if len(filestorage) > 0:
                filenames = ''
                for file in filestorage:
                    filenames += file + '\n'
                    filecontent = filestorage[file]
                    with open(filePath + file, 'w') as Writefile:
                        Writefile.write(filecontent)
                        Writefile.close()
                with open(filePath + 'backup' + datetime.now().strftime('%Y-%m-%d-%H%M%S') +'.txt', 'w') as Backupfile:
                    Backupfile.write(filenames)
                    Backupfile.close()
                print('All Files Backed Up')
            else:
                print('Problem: No Files to Back Up')
        elif Command.startswith('load '):
            backfile = Command.removeprefix('load ')
            with open(filePath + backfile, 'r') as Loadfile:
                filenames = []
                for line in Loadfile:
                    filenames += ["{}".format(line.strip())]
                Loadfile.close()
            for file in filenames:
                try:
                    with open(filePath + file) as Loadfile:
                        filestorage[file] = Loadfile.read()
                    Loadfile.close()
                except:
                    print('Problem: ' + file + ' Was Skipped Because it Could Not be Found')
            print('Files Loaded Sucessfully')
        elif Command.startswith('read '):
            filename = Command.removeprefix('read ')
            print(filestorage[filename])    
     



def main():
    global clients
    Host = '0.0.0.0'
    Port = 12345

    serverSocket.bind((Host, Port))
    serverSocket.listen(5)
    print('Listening for clients to connect...')
    serverMessage = 'Welcome!'

    InputThread = Thread(target=InputListener)
    InputThread.start()

  
    while True:
        Connection, addr = serverSocket.accept()
        clientname = Connection.recv(1024).decode()
        if not clientname in clients:
            clients += [clientname]
            Connection.send('Accept'.encode())
        else:
            Connection.send('Reject'.encode())
        print('Got connection: ' + clientname + ' (' + addr[0] + ')')
        print('Listening for clients to connect...')
        ClientThread = Thread(target=NewClient, args=(Connection,addr,clientname))
        ClientThread.start()
        Connection.send(serverMessage.encode())

if __name__ == '__main__':
    main()