#coding: utf-8
from socket import *
import time
import threading
import sys
import select
from datetime import datetime

def unblock():
    name = blocked.pop(0)
    names_dict.update({name: 0}) 
    
def whoelse(sock,sentence):

    line = "Users currently on: "        
    for i in dataDict.values():
        if list(dataDict.keys())[list(dataDict.values()).index(i)] != sock:
            line = line + "\n" + i
    return line
 
def who_else_since (sock, time):
    print(userTimes)
    sentence = "Since last %d minutes" % int(time)
    for i in userTimes.values():
        cond = True
        command = list(userTimes.keys())[list(userTimes.values()).index(i)]
        if command in dataDict.values():
            curr_sock = list(dataDict.keys())[list(dataDict.values()).index(command)]
            if (curr_sock != sock):
                cond = True
            else: 
                cond = False
        minutes = int((datetime.now() - i).seconds)//60 
        if (minutes < int (time) and cond):
            sentence = sentence + "\n" + command  
    return sentence

def login_check(sock,sentence):
    
    line = sentence
    info = sentence.split()
    name = info[0]
    time = info[1]
    print (name)
    if (name == "whoelsesince"):
        return who_else_since(sock,time)
    
    if name in blocked:
        serverMessage = "You are blocked"
        return serverMessage
        
    password = info[1]
    for j in range (0, len(names)):
        if (name == names[j]):
            if (passwords[j] == password):
                serverMessage="Login Successfull"
                dataDict.update({sock:name})
                userTimes.update({name:datetime.now()})
                break
            else:
                serverMessage="Wrong password"
                counter = names_dict.get(name)
                counter += 1
                if (counter == 3):
                    blocked.append(name)
                names_dict.update({name: counter})
                break
        else :
            serverMessage="Wrong username"
    print(serverMessage)   
    return serverMessage

def logout (sock, sentence):
    #connectionList.remove(sock)
    name = dataDict.get(sock)
    dataDict.pop(sock)
    userTimes.update({name: datetime.now()})
    return "You have been logged out"

def updateTimes():
    for i in dataDict.values():
        userTimes.update({i:datetime.now()})
        
def process(sock,sentence):

    updateTimes()
    if (sentence == "whoelse"):
        return whoelse(sock,sentence)
    elif (sentence == "logout"):
        return logout(sock,sentence)
    else:
        return login_check(sock,sentence)

if __name__ == "__main__":

    serverPort = int(sys.argv[1])
    block = int(sys.argv[2])
    timeout = int(sys.argv[3])
    f = open("Credentials.txt", 'r')
    names = []
    names_dict = {}
    passwords = []
    blocked = []
    clients=[]
    data = f.readlines()
    for i in data :
        line = i.rstrip()
        info = line.split()
        names.append(info[0])
        names_dict.update({info[0]: 0})
        passwords.append(info[1])


    connectionList = []
    dataDict = {}
    userTimes = {}
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(('localhost', serverPort))
    serverSocket.listen(1)
    connectionList.append(serverSocket)
    print "The server is ready to receive"
    
    while 1:
    
        read_sockets,write_sockets,error_sockets = select.select(connectionList,[],[])
        if len(blocked) > 0:
            t = threading.Timer(block, unblock)
            t.start()
        for sock in read_sockets:
            if sock == serverSocket:
                sockfd, addr = serverSocket.accept()
                connectionList.append(sockfd)
            else:
                sentence = sock.recv(1024)
                serverMessage = process(sock,sentence)
                sock.send(serverMessage)
                
    connectionSocket.close()

