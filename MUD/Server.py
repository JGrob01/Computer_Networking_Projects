'''
Created on Nov 2, 2022

@author: John G
'''
import socket
import threading
import BattleRoom
import time

room = BattleRoom.createRoom(.05, 1000)
dict = {}
f = open("output.txt", "w")

#starts the server and creates two threads, one for the battle room and one for processing the clients
def startServer(serverName, serverPort):
   serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   serverSocket.bind((serverName, serverPort))
   print("Hosting on " + str(serverName) + ":" + str(serverPort))
   
   mainThread = threading.Thread(target=processGame, args=(serverSocket, ))
   clientThread = threading.Thread(target=processClients, args=(serverSocket, serverName))
   updateThread = threading.Thread(target=sendClientUpdate, args=(serverSocket, ))
   mainThread.start()
   clientThread.start()
   updateThread.start()

#processes incoming clients and their inputs   
def processClients(serverSocket, serverName):
    global clients, dict
    while True:   
        #Get MSG
        clientMsg = serverSocket.recvfrom(1024)
        #decode msg and addr
        message = clientMsg[0]
        address = clientMsg[1]
        
        #checks if the client address exists
        if not dict.get(address):
            print("adding player from client")
            clientMsg = (message.decode()).split(",")
            player = BattleRoom.Entity(clientMsg[0], int(clientMsg[1]), int(clientMsg[2]), int(clientMsg[3]), float(clientMsg[4]), int(clientMsg[5]), int(clientMsg[6]))
            room.addPlayer(player)
            dict[address] = player
            printToFile("Joined", address, serverName)
        else:
            print("player already here")
            msg = message.decode()
            if msg == "end":
                #print("client wants to end")
                dict.get(address).takeDamage(1000000000000)
                dict.pop(address, None)
            elif int(msg) == 0 or int(msg) == 1 or int(msg) == 2 and dict.get(address).getHealth() != 0:
                #print("player taking action")
                dict.get(address).setAction(int(msg))
                printToFile(player.getAction(), address, serverName)
            else:
                #print("take no action")
                dict.get(address).setAction(-1)
                printToFile("No Action", address, serverName)

#Helper to send clients updates
def sendClientUpdate(serverSocket):
    while True:
        time.sleep(1)
        for x in dict:
            #print("send updates")
            msg = "Your health is " + str(dict.get(x).getHealth())
            serverSocket.sendto(msg.encode(), x) 
            if dict.get(x).getHealth() == 0:
                msg = "dead"
                serverSocket.sendto(msg.encode(), x)
                dict.pop(x, None)
                break

#run the battle room   
def processGame(serverSocket):
    BattleRoom.runGame(room)
     
    
#prints the Player, move, IP From, IP To to file
def printToFile(action, ipf, ipt):
    f = open("output.txt", "a")
    f.write("Action:" + str(action) + " From IP:" + str(ipf) + " To IP:" + str(ipt))
    f.write("\n")

if __name__ == "__main__":
    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)
    startServer(IPAddr, 4446)
