#coding: utf-8
from socket import *
import sys
import thread


# A threading call which runs to be open for any input by the client
# and sends it to the server.
def takeMessages():
    while 1:
        message = raw_input('Command :')
        try:
            clientSocket.send(message)
        except:
            break
    return   
    
# Recieves replies from the server at any given time and checks if it's a 
# logout call, if not prints it or closes the socket if it is.
def rcv_commands():
    stop_thread = False
    thread.start_new_thread (takeMessages,())
    while 1:
        sentence = clientSocket.recv(1024)
        message = sentence
        if (sentence == "Force Logout"):
            print sentence
            clientSocket.close()
            break
        elif (sentence == "Logged out"):
            print 'From Server:', sentence
            clientSocket.close()
            break
        else:
            print 'From Server:', sentence
    
    return "logout"        

# A simple method which takes user input and sends it as a concatenated string
# to the server. Also check if the server reply is succesfull or not.
def login(): 
    count = 0
    stop_thread = True
    name = raw_input('Username :')
    if " " in name:
        print "name can't have a whitespace, try again"
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
        message = rcv_commands()
    else:
        login()

def main():
    serverName = sys.argv[1]
    serverPort = int(sys.argv[2])
    clientSocket = create_connection((serverName, serverPort))
    login()
if __name__ == "__main__":
    
    serverName = sys.argv[1]
    serverPort = int(sys.argv[2])
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))
    login()


