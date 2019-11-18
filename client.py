#coding: utf-8
from socket import *
import sys
import thread

def takeMessages(stop_thread):
    while 1:
        message = raw_input('Command :')
        if stop_thread:
            break
        try:
            clientSocket.send(message)
        except:
            break
    return   
    
def rcv_commands(stop_thread):
    stop_thread = False
    thread.start_new_thread (takeMessages,(stop_thread,))
    while 1:
        sentence = clientSocket.recv(1024)
        message = sentence
        if (sentence == "Force Logout"):
            print sentence
            clientSocket.close()
        elif (sentence == "Logged out"):
            print 'From Server:', sentence
            clientSocket.close()
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
        rcv_commands(stop_thread)
    else:
        login()

def main():

    serverName = 'localhost'
    serverPort = int(sys.argv[1])
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))
    login()

if __name__ == "__main__":
    
    serverName = 'localhost'
    serverPort = int(sys.argv[1])
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))
    login()


