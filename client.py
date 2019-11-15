#coding: utf-8
from socket import *
import sys
import thread
stop_thread = False

def takeMessages(message):
    while 1:
        if (message == "login"):
            break
        message = raw_input('Command :')
        if stop_thread:
            break
        clientSocket.send(message)
    return   
    
def rcv_commands():
    message = ""
    thread.start_new_thread (takeMessages,(message,))
    while 1:
        sentence = clientSocket.recv(1024)
        message = sentence
        if (sentence == "Force Logout"):
            print sentence
            message = "login"
            login()
        elif (sentence == "Logged out"):
            print 'From Server:', sentence
            login()   
        else:
            print 'From Server:', sentence
    return        

def login(): 
    count = 0
    stop_thread = True
    name = raw_input('Username :')
    password = raw_input('Password :')
    sentence = name + " " + password
    
    if (sentence == None):
        clientSocket.close()
    
    clientSocket.send(sentence)

    modifiedSentence = clientSocket.recv(1024)
    print 'From Server:', modifiedSentence
    l1 = modifiedSentence.split() 
    if "Successfull" in l1:
        rcv_commands()
    else:
        login()

if __name__ == "__main__":

    serverName = 'localhost'
    serverPort = int(sys.argv[1])
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))
    login()


