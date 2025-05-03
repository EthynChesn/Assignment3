from socket import *
from threading import *
import sys

def put(filename):
    try:
        file = open(filename,'r')
    except FileNotFoundError:
        print('Error: Directory and/or File Not Found')
    except PermissionError:
        print('Error: No permission to access Directory and/or File')
    else:
        Char = filename[-1]
        Counter = -1
        Handler = False
        while not Char == "\\":
            Counter -= 1
            try:
                Char = filename[Counter]
            except:
                print('Error Uploading File')
                Handler = True
                break
        if not Handler:
            clientSocket.send('put'.encode())
            shortname = ''
            for index in range(Counter+1,-1):
                shortname += filename[index]
            shortname += filename[-1]
            filecontent = file.read()
            clientSocket.send(shortname.encode())
            clientSocket.send(filecontent.encode())
            print('Succesfully Uploaded ' + filename)
            file.close()
    

def get(getfilename):
    global filePath
    Request = getfilename
    clientSocket.send('get'.encode())
    clientSocket.send(Request.encode())
    filecontent = clientSocket.recv(1024).decode()
    if filecontent == 'error':
        print('Error: File Not Found')
    else:
        with open(filePath+getfilename, 'w') as Writefile:
            Writefile.write(filecontent)
        print(getfilename + " Downloaded succesfully")
        Writefile.close()


def InputListener():
    global Close
    Message = input()
    if Message.startswith('put '):
        put(Message.removeprefix('put '))

    elif Message.startswith('get '):
        get(Message.removeprefix('get '))

    elif Message == 'list':
        clientSocket.send('list'.encode())
        listlength = clientSocket.recv(1024).decode()
        clientSocket.send('True'.encode())    
        listlength = int(listlength)
        if listlength == 0:
            print("Error: No Files Found on Server")
        else:
            print('List of Files on the Server:')
            for filelist in range(listlength):
                file = clientSocket.recv(1024).decode()
                print(file)
                clientSocket.send('True'.encode())

    elif Message.startswith('delete '):
        clientSocket.send('delete'.encode())
        Acknowledge = clientSocket.recv(1024).decode()
        if Acknowledge == 'True':
            clientSocket.send(Message.removeprefix('delete ').encode())
        outcome = clientSocket.recv(1024).decode()
        if outcome == 'deleted':
            print(Message.removeprefix('delete ') + ' succesfully deleted from Server')
        else:
            print('Error: File Not Found on Server')

    elif Message == 'close':
        clientSocket.send('close'.encode())
        Acknowledge = clientSocket.recv(1024).decode()
        if Acknowledge == 'True':
            clientSocket.close()
            Close = True
    
    elif Message.startswith('rename '):
        clientSocket.send('rename'.encode())
        Acknowledge = clientSocket.recv(1024).decode()
        if Acknowledge == 'True':
            try:
                oldName, newName = Message.removeprefix('rename ').split()
                clientSocket.send(oldName.encode())
                clientSocket.send(newName.encode())
                outcome = clientSocket.recv(1024).decode()
                if outcome == 'renamed':
                    print('File has been successfully renamed')
                else:
                    print('Error: File Not Found on Server')
            except ValueError:
                print("Error: Please try again, format as 'rename (old file name) (new file name)")

    elif Message == 'help':
        print('Commands:\nput <DriveName:\\filepath\\filename>\nget <filename>\ndelete <filename>\nrename <old filename> <new filename>\nlist\nclose')


filePath = r'E:\\'
hostname = gethostname()
IPAddr = gethostbyname(hostname)
Server = '10.200.4.67'
Port = 12345

#Create socket
clientSocket = socket(AF_INET, SOCK_STREAM)

#Connect client to server
clientSocket.connect((Server, Port))

#Receive and print initial information
print(clientSocket.recv(1024).decode())

Close = False
while True:
    InputThread = Thread(target=InputListener)
    InputThread.start()
    if Close == True:
        break

print('Disconnected from Server')
sys.exit()