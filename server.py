#coding: utf-8
from socket import *
import time
import threading
import thread
import sys
import select

from datetime import datetime

def unblock():
    name = blocked.pop(0)
    names_dict.update({name: 0})
    t.cancel() 
    
def whoelse(sock,sentence):

    line = "\nUsers currently on: "        
    for i in dataDict.values():
        if list(dataDict.keys())[list(dataDict.values()).index(i)] != sock:
            line = line + "\n" + i
    return line
 
def who_else_since (sock, time):
    print(userTimes)
    sentence = "\nSince last %d minutes" % int(time)
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

def broadcast(sock, line):
    br = line.split(" ",1)[1]
    message = "\nBroadcast Message: " + br
    for i in dataDict.keys():
        if i != sock:
            i.send(message)
    
    return "Message Sent" 
    
def messaging(sock, line):
    splits = line.split(" ", 2)
    reciever = splits[1]
    sending = splits[2]
    sent = False
    message = "From %s: " % dataDict.get(sock) + sending
    for i in dataDict.keys():
        if dataDict.get(i) == reciever:
            i.send(message)
            sent = True
    
    if sent == True:
        return "Message delivered"
    else:
        return "User not found"
    
def login_check(sock,sentence):
    
    line = sentence
    info = sentence.split()
    name = info[0]
    time = info[1]
    print (name)
    if (name == "whoelsesince"):
        return who_else_since(sock,time)
    elif (name == "broadcast"):
        return broadcast(sock, line)
    elif (name == "message"):
        return messaging(sock,line)
    
    if name in blocked:
        serverMessage = "You are blocked"
        return serverMessage
    
    if name in dataDict.values():
        serverMessage = "Already logged in"
        return serverMessage
    
    presence = "\nNow up: "
    password = info[1]
    for j in range (0, len(names)):
        if (name == names[j]):
            if (passwords[j] == password):
                serverMessage="Login Successfull"
                
                dataDict.update({sock:name})
                userTimes.update({name:datetime.now()})
                lastActivity.update({sock:datetime.now()})

                presence = presence + dataDict.get(sock)                 
                for e in dataDict.keys():
                    if e != sock:
                        e.send(presence) 
                break
            else:
                serverMessage="Wrong password"
                counter = names_dict.get(name)
                counter += 1
                if (counter >= 3):
                    serverMessage="You are blocked"
                    blocked.append(name)
                    #connectionList.remove(sock)
                names_dict.update({name: counter})
                break
        else :
            serverMessage="Wrong username"
    return serverMessage

def logout (sock, sentence):
    name = dataDict.get(sock)
    dataDict.pop(sock)
    userTimes.update({name: datetime.now()})
    return "Logged out"
    
def force_logout (sock):
    sock.send("Force Logout")
    dataDict.pop(sock)
    lastActivity.pop(sock)

def update_times():
    for i in dataDict.values():
        userTimes.update({i:datetime.now()})
        
def last_activity_update(sock):
    lastActivity.update({sock:datetime.now()})
    
def process(sock,sentence):

    update_times()
    last_activity_update(sock)
    if (sentence == "whoelse"):
        return whoelse(sock,sentence)
    elif (sentence == "logout"):
        return logout(sock,sentence)
    else:
        return login_check(sock,sentence)
      
def check_offlines(timeout):
    while 1:
        print(dataDict)
        for i in dataDict.keys():    
            if (lastActivity.get(i) == None): continue
            seconds = int((datetime.now() - lastActivity.get(i)).seconds) 
            if seconds > int(timeout):
                force_logout(i)
        time.sleep(1)
        

if __name__ == "__main__":

    serverPort = int(sys.argv[1])
    block = int(sys.argv[2])
    timeout = int(sys.argv[3])
    f = open("Credentials.txt", 'r')
    names = []
    names_dict = {}
    passwords = []
    data = f.readlines()
    for i in data :
        line = i.rstrip()
        info = line.split()
        names.append(info[0])
        names_dict.update({info[0]: 0})
        passwords.append(info[1])
    
    blocked = []
    connectionList = []
    dataDict = {}
    userTimes = {}
    lastActivity = {}
    
    thread.start_new_thread (check_offlines,(timeout,))
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
                try:
                    sentence = sock.recv(1024)
                    print sentence
                    serverMessage = process(sock,sentence)
                    sock.send(serverMessage)
                except:
                    print "Nothing rcvd"
    connectionSocket.close()
