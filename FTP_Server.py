from socket import *
from threading import *
from datetime import datetime
import sys

#Storage
clients = []
fileStorage = {}
connections = []


#Wait to Send Next File Name to Client (List command)
def WaitNext(clientSocket):
    if clientSocket.recv(1024).decode() == 'True':
        return

#Main Client Thread
def NewClient(clientSocket, address):
    global clients
    global connections
    connections += [clientSocket]
    clientName = clientSocket.recv(1024).decode()
    clients += [(clientName,address[0])]

    while True:
        incomingCommand = clientSocket.recv(1024).decode()
        #Put command
        if incomingCommand == 'put':
            fileName = clientSocket.recv(1024).decode()
            fileContent = clientSocket.recv(1024).decode()
            fileStorage[fileName] = fileContent
            print(clientName[0] + ' (' + clientName[1] + ')' + " Uploaded " + fileName)
        #Get command
        if incomingCommand == 'get':
            fileName = clientSocket.recv(1024).decode()
            print(address[0] + ' requested ' + fileName)
            if not fileName in fileStorage:
                print(clientName[0] + ' (' + clientName[1] + ')' + ' Problem: ' + fileName + " Not Found" )
                clientSocket.send('error'.encode())
            else:
                file = fileStorage[fileName]
                clientSocket.send(file.encode())
        #List command
        if incomingCommand == 'list':
            storageLength = str(len(fileStorage))  
            clientSocket.send(storageLength.encode())
            if len(fileStorage) > 0:
                Acknowledge = clientSocket.recv(1024).decode()
                if Acknowledge == 'True':
                    for file in fileStorage:
                        clientSocket.send(file.encode())
                        WaitNext(clientSocket)
                Acknowledge = False
        #Delete command
        if incomingCommand == 'delete':
            clientSocket.send('True'.encode())
            fileName = clientSocket.recv(1024).decode()
            print(clientName[0] + ' (' + clientName[1] + ')' + ' is attempting to delete ' + fileName)
            if fileName in fileStorage:
                del fileStorage[fileName]
                clientSocket.send('deleted'.encode())
                print(fileName + ' deleted by ' + clientName[0] + ' (' + clientName[1] + ')')
            else:
                clientSocket.send('error'.encode())
                print(clientName[0] + ' (' + clientName[1] + ')' + ' Problem: ' + fileName + ' Not Found')
        #Close command
        if incomingCommand == 'close':
            clientSocket.send('True'.encode())
            clientSocket.close()
            print(clientName[0] + ' (' + clientName[1] + ')' + ' has disconnected')
            break
        #Rename command
        if incomingCommand == 'rename':
            clientSocket.send('True'.encode())
            oldName = clientSocket.recv(1024).decode()
            newName = clientSocket.recv(1024).decode()
            if oldName in fileStorage:
                fileStorage[newName] = fileStorage.pop(oldName)
                clientSocket.send('renamed'.encode())
                print(f"{clientName[0] + ' (' + clientName[1] + ')'} renamed {oldName} to {newName}")
            else:
                clientSocket.send('error'.encode())
                print(clientName[0] + ' (' + clientName[1] + ')' + ' Problem: ' + fileName + ' Not Found')

#Listen for Server Input, listen for certain commands.
def InputListener():
    global connections
    filePath = r'' #Replace with Server File Path (Root of Drive Recommended)
    while True:
        command = input()
        #List Files command
        if command == "listfiles":
            if len(fileStorage) > 0:
                print('List of Files on Server:')
                for file in fileStorage:
                    print(file)
            else:
                print('Problem: List of Files is Empty')
        #List Users command
        elif command == "listusers":
            if len(clients) > 0:
                print('List of Users Connected to Server:')
                for client in clients:
                    print(client[0] + ' (' + client[1] + ')')
            else:
                print('Problem: No Users are Currently Connected')
        #Delete command
        elif command.startswith('delete '):
            fileName = command.removeprefix('delete ')
            if fileName in fileStorage:
                del fileStorage[fileName]
                print('deleted ' + fileName)
            else:
                print('Problem: File Not Found')
        #Backup command
        elif command == 'backup':
            if len(fileStorage) > 0:
                fileNames = ''
                for file in fileStorage:
                    fileNames += file + '\n'
                    fileContent = fileStorage[file]
                    with open(filePath + file, 'w') as writeFile:
                        writeFile.write(fileContent)
                        writeFile.close()
                with open(filePath + 'backup' + datetime.now().strftime('%Y-%m-%d-%H%M%S') +'.txt', 'w') as backupFile:
                    backupFile.write(fileNames)
                    backupFile.close()
                print('All Files Backed Up')
            else:
                print('Problem: No Files to Back Up')
        #Load command
        elif command.startswith('load '):
            backfile = command.removeprefix('load ')
            with open(filePath + backfile, 'r') as loadFile:
                fileNames = []
                for line in loadFile:
                    fileNames += ["{}".format(line.strip())]
                loadFile.close()
            for file in fileNames:
                try:
                    with open(filePath + file) as loadFile:
                        fileStorage[file] = loadFile.read()
                    loadFile.close()
                except:
                    print('Problem: ' + file + ' Was Skipped Because it Could Not be Found')
            print('Files Loaded Sucessfully')
        #Read command
        elif command.startswith('read '):
            fileName = command.removeprefix('read ')
            print(fileStorage[fileName])
        #Close command
        elif command == 'close':
            print('Server Shutting Down')
            for connection in connections:
                connection.close()
            serverSocket.close()
            sys.exit()

#Main Function
def main():
    #Initiliazation
    Host = '0.0.0.0'
    Port = 12345
    
    serverSocket.bind((Host, Port))
    serverSocket.listen(5)

    print('Listening for clients to connect...')
    serverMessage = 'Welcome! Type "help" to see a list of commands.'

    inputThread = Thread(target=InputListener)
    inputThread.start()

    #Main Loop
    while True:
        connection, address = serverSocket.accept()
        print('Got connection: ' + str(address))
        print('Listening for clients to connect...')
        clientThread = Thread(target=NewClient, args=(connection,address))
        clientThread.start()
        connection.send(serverMessage.encode())

#Start

    #Create Socket
serverSocket = socket(AF_INET, SOCK_STREAM)

if __name__ == '__main__':
    main()