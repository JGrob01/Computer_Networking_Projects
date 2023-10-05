'''
Created on Nov 2, 2022

@author: John G
'''
import socket
import time
import threading

serverAddr = (" ", 0)

playerName = ""
currentHealth = 0
maxHealth = 0
damage = 0
hitChance = 0           #DOESNT WORK WE DO NOT NEED
attackRate = 0          #In terms of milliseconds, how often a hero or enemy can attack someone.
healRate = 0            #In terms of milliseconds, how often a hero or enemy can heal damage.
action = 0              #Do Nothing (-1), Defend (0), Attack (1), or Heal (2)


#connect the client to the host
def connectClient(serverName, serverPort):
    global serverAddr, currentHealth, maxHealth
    serverAddr = (serverName, serverPort)
    
    debugPlayer()   #these are set values for debugging only
    #createPlayer() ENABLE THIS WHEN NOT TEXTING
    
    clientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    msg = playerName + "," + str(maxHealth) + "," + str(maxHealth) + "," + str(damage) + "," + str(hitChance) + "," + str(attackRate) + "," + str(healRate)
    currentHealth = maxHealth
    clientSocket.sendto(msg.encode(), serverAddr)
    
    gameThread = threading.Thread(target=processGame, args=(clientSocket,))
    msgThread = threading.Thread(target=processServerMsgs, args=(clientSocket,))
    gameThread.start()
    msgThread.start()

#creates a debug player that I don't have to put inputs
def debugPlayer():
    global playerName, maxHealth, currentHealth, maxHealth, damage, attackRate, healRate, hitChance
    playerName = "BOT"
    maxHealth = 500
    currentHealth = maxHealth
    damage = 10
    hitChance = 1
    attackRate = 1000
    healRate = 5000

#you create the player
def createPlayer():
    global playerName, maxHealth, currentHealth, damage, attackRate, healRate
    playerName = input('Input your player name')
    maxHealth = input('Input your max health')
    currentHealth = maxHealth
    damage = input('Input the amount of damage your player deals') 
    attackRate = input('Input the amount of time in milliseconds your player can attack') 
    healRate = input('Input the amount of time in milliseconds your player can heal') 
    
#Processes the client input to send to the server
def processGame(clientSocket):
    global serverAddr, currentHealth, maxHealth
    while True:
        x = input('Input an action. Do Nothing (-1), Defend (0), Attack (1), Heal (2), End Connection (end)\n')
        if currentHealth == 0:
            break
        clientSocket.sendto(x.encode(), serverAddr)
        if(x == "end"):
            break
    resetClient(clientSocket)

#processes incoming server messages and prints
def processServerMsgs(clientSocket): 
    global serverAddr, currentHealth, maxHealth 
    while True:
        serverMSG = clientSocket.recvfrom(1024) 
        message = serverMSG[0]
        if message.decode() == "dead":
            currentHealth = 0
            print("You are dead\n")
            print("Please press enter\n")
            break
        print(message.decode()) 

#resets the client on death or disconnect
def resetClient(clientSocket):
    global serverAddr, currentHealth, maxHealth
    x = input('Do you want to rejoin? y/n\n')
    if(x == "y"):
        msg = playerName + "," + str(maxHealth) + "," + str(maxHealth) + "," + str(damage) + "," + str(hitChance) + "," + str(attackRate) + "," + str(healRate)
        clientSocket.sendto(msg.encode(), serverAddr)
        gameThread = threading.Thread(target=processGame, args=(clientSocket,))
        msgThread = threading.Thread(target=processServerMsgs, args=(clientSocket,))
        currentHealth = maxHealth
        gameThread.start()
        msgThread.start()

if __name__ == "__main__":
    x = input('Input the host IP, make sure the server has started the game')
    connectClient(x, 4446)
    
    