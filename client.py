#coding: utf-8
from socket import *
import sys

def takeMessages():
    message = raw_input('Command :')
    line = message
    
    while 1:
        if (message == "logout"):
            logout()        
        elif (message == "quit"):
            clientSocket.close()
        elif (message == "whoelse"):
            whoelse()
        elif (line.split()[0] == "whoelsesince") :
            whoelsesince(message)
def logout():
    clientSocket.send("logout")
    modifiedSentence = clientSocket.recv(1024)
    print 'From Server:', modifiedSentence
    login()   
         
def whoelse():
    clientSocket.send("whoelse")
    modifiedSentence = clientSocket.recv(1024)
    print 'From Server:', modifiedSentence
    takeMessages()
    
def whoelsesince(message):
    clientSocket.send(message)
    sentence = clientSocket.recv(1024)
    print 'From Server:', sentence
    takeMessages()
    
def login(): 
    count = 0
    name = raw_input('Username :')
    password = raw_input('Password :')
    sentence = name + " " + password
    
    if (sentence == None):
        clientSocket.close()
    
    clientSocket.send(sentence)

    modifiedSentence = clientSocket.recv(1024)
    
    print 'From Server:', modifiedSentence
    if (modifiedSentence == "Login Successfull"):
        takeMessages()
    else:
        login()

if __name__ == "__main__":

    serverName = 'localhost'
    serverPort = int(sys.argv[1])
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))
    login()


