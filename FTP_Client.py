from socket import *
from threading import *
import sys

#Put Function. Open file, seperate file name from path, send fileName and contents of file to Server. 
def PutFile(fileName):
    try:
        file = open(fileName,'r')
    except FileNotFoundError:
        print('Error: Directory and/or File Not Found')
    except PermissionError:
        print('Error: No permission to access Directory and/or File')
    else:
        character = fileName[-1]
        counter = -1
        handler = False
        while not character == "\\":
            counter -= 1
            try:
                character = fileName[counter]
            except:
                print('Error Uploading File')
                handler = True
                break
        if not handler:
            clientSocket.send('put'.encode())
            shortName = ''
            for index in range(counter+1,-1):
                shortName += fileName[index]
            shortName += fileName[-1]
            fileContent = file.read()
            clientSocket.send(shortName.encode())
            clientSocket.send(fileContent.encode())
            print('Succesfully Uploaded ' + fileName)
            file.close()
    
#Get Function. Get file from server, write to Client computer.
def GetFile(getFileName):
    global filePath
    requestFile = getFileName
    clientSocket.send('get'.encode())
    clientSocket.send(requestFile.encode())
    fileContent = clientSocket.recv(1024).decode()
    if fileContent == 'error':
        print('Error: File Not Found')
    else:
        with open(filePath+getFileName, 'w') as writeFile:
            writeFile.write(fileContent)
        print(getFileName + " Downloaded succesfully")
        writeFile.close()

#Listen for User input, listen for certain commands.
def InputListener():
    global connectionClosed
    userMessage = input()
    #Put Command
    if userMessage.startswith('put '):
        PutFile(userMessage.removeprefix('put '))
    #Get Command
    elif userMessage.startswith('get '):
        GetFile(userMessage.removeprefix('get '))
    #List Command
    elif userMessage == 'list':
        clientSocket.send('list'.encode())
        listLength = clientSocket.recv(1024).decode()
        clientSocket.send('True'.encode())    
        listLength = int(listLength)
        if listLength == 0:
            print("Error: No Files Found on Server")
        else:
            print('List of Files on the Server:')
            for filelist in range(listLength):
                file = clientSocket.recv(1024).decode()
                print(file)
                clientSocket.send('True'.encode())
    #Delete Command
    elif userMessage.startswith('delete '):
        clientSocket.send('delete'.encode())
        Acknowledge = clientSocket.recv(1024).decode()
        if Acknowledge == 'True':
            clientSocket.send(userMessage.removeprefix('delete ').encode())
        outcome = clientSocket.recv(1024).decode()
        if outcome == 'deleted':
            print(userMessage.removeprefix('delete ') + ' succesfully deleted from Server')
        else:
            print('Error: File Not Found on Server')
    #connectionClosed Command
    elif userMessage == 'close':
        clientSocket.send('close'.encode())
        Acknowledge = clientSocket.recv(1024).decode()
        if Acknowledge == 'True':
            clientSocket.close()
            connectionClosed = True
    #Rename Command
    elif userMessage.startswith('rename '):
        clientSocket.send('rename'.encode())
        Acknowledge = clientSocket.recv(1024).decode()
        if Acknowledge == 'True':
            try:
                oldName, newName = userMessage.removeprefix('rename ').split()
                clientSocket.send(oldName.encode())
                clientSocket.send(newName.encode())
                outcome = clientSocket.recv(1024).decode()
                if outcome == 'renamed':
                    print('File has been successfully renamed')
                else:
                    print('Error: File Not Found on Server')
            except ValueError:
                print("Error: Please try again, format as 'rename (old file name) (new file name)")
    #Help Command
    elif userMessage == 'help':
        print('Commands:\nput <DriveName:\\filepath\\fileName>\nget <fileName>\ndelete <fileName>\nrename <old fileName> <new fileName>\nlist\nclose')

#Client Information
filePath = r'E\\' #Replace with Client File Path (Root of Drive Recommended)
Server = '10.200.4.67' #Replace with Server IP
Port = 12345

while True:
    username = input('Enter Username: ').strip()
    if username:
        break
    else:
        print('Username Cannot be Empty. Please Try Again.')

#Create socket
clientSocket = socket(AF_INET, SOCK_STREAM)

#Connect client to server
clientSocket.connect((Server, Port))

clientSocket.send(username.encode())

#Receive and print initial information
print(clientSocket.recv(1024).decode())

#Main Loop
connectionClosed = False
while True:
    inputThread = Thread(target=InputListener)
    inputThread.start()
    if connectionClosed == True:
        break

print('Disconnected from Server')
sys.exit()