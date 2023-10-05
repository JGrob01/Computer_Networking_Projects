'''
Created on Oct 18, 2022

@author: John Grobaker
'''
import socket
import time


#connect the client to the host
def connectClient(hostName, hostPort):
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((hostName, hostPort))
    msg = "HELLO"
    clientSocket.send(msg.encode())
    print("Welcome to the game")
    processGame(clientSocket)


#Processes the client/server messages
def processGame(clientSocket):
    lock = 0
    while True:
        #GET THE LOCK FROM THE SERVER
        serverMsg = clientSocket.recv(4096)
        msg = serverMsg.decode('utf8', 'ignore')
        if serverMsg and msg[0] == "1":
            newServerMsg = clientSocket.recv(4096)
            newMsg = newServerMsg.decode('utf8', 'ignore')
            #GET THE STATUS OF GAME FROM SERVER
            if newMsg == "X won":
                winMsg = clientSocket.recv(4096)
                winBoard = winMsg.decode('utf8', 'ignore')
                print(winBoard)
                print("Player X has won the game")
                break
            elif newMsg == "O won":
                winMsg = clientSocket.recv(4096)
                winBoard = winMsg.decode('utf8', 'ignore')
                print(winBoard)
                print("Player O has won the game")
                break
            elif newMsg == "Garb":
                move = input("Please enter a better move")
                clientSocket.send(str(move).encode())
            else:
                #Print the board, get user input
                print(newMsg)
                move = input(
                    "Enter a move, coordinates A1,A2,A3,B1,B2,B3,C1,C2,C3")
                #send the lock and player move back to the server
                msgLock = '1'
                clientSocket.send(msgLock.encode())
                time.sleep(1)
                clientSocket.send(str(move).encode())
        else:
            print("Waiting for opponent")
        lock = 0

    #RESETTING THE GAME
    resetMSG = input("Would you like to play again? y/n")
    clientSocket.send(resetMSG.encode("utf-8"))
    resetServerMsg = clientSocket.recv(4096)
    if resetServerMsg.decode("utf-8") == "y":
        msg = "HELLO"
        clientSocket.send(msg.encode())
        print("Resetting Game")
        processGame(clientSocket)
    else:
        clientSocket.close()


if __name__ == "__main__":
    x = input('Input the host IP, make sure the server has started the game')
    connectClient(x, 4446)

