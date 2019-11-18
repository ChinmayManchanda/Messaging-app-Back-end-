#coding: utf-8
from socket import *
import time
import threading
import thread
import sys
import select

from datetime import datetime

# Unblock call to unblock a user (for the wrong password case)
def unblock():
    name = blocked.pop(0)
    names_dict.update({name: 0})
    t.cancel() 
    
# Checks and returns the names of the user's who are still online.
def whoelse(sock,sentence):

    line = "\nUsers currently on: "        
    for i in dataDict.values():
        if list(dataDict.keys())[list(dataDict.values()).index(i)] != sock:
            line = line + "\n" + i
    return line
 
# Checks and returns the names of users who have been online for the last "time"
# seconds.
def who_else_since (sock, time):
    print(userTimes)
    sentence = "\nSince last %d seconds" % int(time)
    for i in userTimes.values():
        cond = True
        command = list(userTimes.keys())[list(userTimes.values()).index(i)]
        if command in dataDict.values():
            curr_sock = list(dataDict.keys())[list(dataDict.values()).index(command)]
            if (curr_sock != sock):
                cond = True
            else: 
                cond = False
        seconds = int((datetime.now() - i).seconds) 
        if (seconds < int (time) and cond):
            sentence = sentence + "\n" + command  
    return sentence


# Function call to broadcast a message to all online users.
def broadcast(sock, line):
    br = line.split(" ",1)[1]
    message = "\nBroadcast Message: " + br
    for i in dataDict.keys():
        if i != sock:
            i.send(message)
    
    return "Message Sent" 
    
# This function is responsible for sending messages from one client to another
# and also stores a message if the reciever is offline.
def messaging(sock, line):
    splits = line.split(" ", 2)
    reciever = splits[1]
    sending = splits[2]
    sent = False
    message = "From %s: " % dataDict.get(sock) + sending
    
    if dataDict.get(sock) in blockDict.get(reciever):
        return "User not found"
    

    for i in dataDict.keys():
        if dataDict.get(i) == reciever:
            i.send(message)
            sent = True
    
    if sent == True:
        return "Message delivered"
    else:
        if reciever in names:
            if reciever in offlineStore:
                offlineStore[reciever].append(message)
            else:
                offlineStore[reciever] = message
            return "User is offline"
        else:
            return "User not found"
    
# Function call to block a valid user.
def block_user(sock,line):
    l1 = line.split()
    to_block = l1[1]
    if to_block in names and to_block != dataDict.get(sock):
        if dataDict.get(sock) in blockDict:
            blockDict[dataDict.get(sock)].append(to_block)
        else:
            blockDict[dataDict.get(sock)] = [to_block] 
        serverMessage = " %s has been blocked" % to_block
    else:
        serverMessage = "Unknown user."    

    return serverMessage

# Function call to unblock a blocked user.
def unblock_user(sock,line):
    l1 = line.split()
    to_unblock = l1[1]
    if dataDict.get(sock) in blockDict:
        if to_unblock in blockDict.get(dataDict.get(sock)):
            blockDict.get(dataDict.get(sock)).remove(to_unblock)
            serverMessage = " %s has been un blocked" % to_unblock
            
    else:
        serverMessage = "Unknown user."    

    return serverMessage
        
        
# This function has various responsibilities:
# (1) Checks the credentials and logs sends back an appropiate message.
# (2) Is responsible for sending the presence notification to all other clients.
# (3) Checks and sends offline messages whenever a user logs in.
def login_check(sock,sentence):
    
    line = sentence
    info = sentence.split()
    
    name = info[0]
    password = info[1]
    
    if name in blocked:
        serverMessage = "You are blocked"
        return serverMessage
    
    if name in dataDict.values():
        serverMessage = "Already logged in"
        return serverMessage
    
    presence = "\nNow up: "
    for j in range (0, len(names)):
        if (name == names[j]):
            if (passwords[j] == password):
                serverMessage="Login Successfull"
                
                dataDict.update({sock:name})
                userTimes.update({name:datetime.now()})
                lastActivity.update({sock:datetime.now()})

                presence = presence + dataDict.get(sock)                 
                message = " "
                for offm in offlineStore.get(name):
                    message += offm + "\n"
                    
                
                
                for e in dataDict.keys():
                    if e != sock and dataDict.get(e) not in blockDict.get(name):
                        e.send(presence) 
                break
            else:
                serverMessage="Wrong password"
                counter = names_dict.get(name)
                counter += 1
                if (counter >= 3):
                    serverMessage="You are blocked"
                    blocked.append(name)
                names_dict.update({name: counter})
                break
        else :
            serverMessage="Wrong username"
    return serverMessage + "\n" + message

# Processes a logout request from the client and removes the client from
# server logs.
def logout (sock, sentence):
    name = dataDict.get(sock)
    dataDict.pop(sock)
    userTimes.update({name: datetime.now()})
    return "Logged out"
 
# Sends a force logout message to the client if the client has been 
# offline for more than the "timeout" time.   
def force_logout (sock):
    sock.send("Force Logout")
    dataDict.pop(sock)
    lastActivity.pop(sock)
    sockfd = int(sock)
    connectionList.pop(sockfd)
    
# Updates times for all logged in users who are still online.
def update_times():
    for i in dataDict.values():
        userTimes.update({i:datetime.now()})
        
# Updates the last time the client made a request.
def last_activity_update(sock):
    lastActivity.update({sock:datetime.now()})
    
    
# Function calls different functions to process the 
# recieved message from the client.
def process(sock,sentence):

    update_times()
    message = None;
    last_activity_update(sock)
    if (sentence == "whoelse"):
        message = whoelse(sock,sentence)
    elif (sentence == "logout"):
        message = logout(sock,sentence)
    else:
        line = sentence
        info = sentence.split()
        if (info[0] == "whoelsesince"):
            time = info[1]
            message = who_else_since(sock,time)
        elif (info[0] == "broadcast"):
            message = broadcast(sock, line)
        elif (info[0] == "message"):
            message = messaging(sock,line)
        elif (info[0] == "block"):
            message = block_user(sock, line)
        elif (info[0] == "unblock"):
            message = unblock_user(sock,line)
        else:
            message = login_check(sock,line)
        
    return message
    
    
# A thread call that checks every second if any user has exceeded the timeout 
# limit and calls the force_logout() function if true.    
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
    blockDict = {}
    offlineStore = {} 
    for i in names:
        blockDict[i] = []
        offlineStore[i] = []    
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
                print sockfd
                connectionList.append(sockfd)
            else:
                try:
                    sentence = sock.recv(1024)
                except:                    
                    print "Invalid Command"
                serverMessage = process(sock,sentence)
                sock.send(serverMessage)
    connectionSocket.close()

