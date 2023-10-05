'''
Created on Oct 18, 2022

@author: John Grobaker
'''
import socket
import threading
import TicTacToe
import time

game = TicTacToe.TicTacToe()
clients = []
reset_count = 0
f = open("output.txt", "w")


#starts the server
def hostGame(hostName, hostPort):
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind((hostName, hostPort))
    print("Hosting on " + str(hostName) + ":" + str(hostPort))
    serverSocket.listen(2)
    processClients(serverSocket, " ")


#the server will listen for 2 incoming clients
#when each connects they will get their respective messages
def processClients(serverSocket, a):
    count = 0
    player_turn = 0
    while True:
        if count < 2:
            clientSocket, clientAddr = serverSocket.accept()
            clients.append(clientSocket)
            count += 1
            if count == 1:
                player_turn = 1
            else:
                player_turn = 0
            print(clientAddr)
            #clientSocket.settimeout(30)
            threading.Thread(target=processClientMsg,
                             args=(clientSocket, player_turn)).start()


#Processes the client/server messages
def processClientMsg(clientSocket, player_turn):
    global reset_count
    clientSocket.recv(4096)  #Welcome Message from clients
    while len(clients) != 2:
        True
    game.setPlayer(1)
    while True:
        if game.checkForWin():
            break
        if player_turn == game.getPlayer():
            #send the lock and gameboard to the client
            sendMsgToClient(clientSocket, "1")
            time.sleep(1)
            gameboard = game.toString()
            clientSocket.send(gameboard.encode())
            #wait for client input, this is the move the client makes
            clientSocket.recv(4096)  #process lock return
            clientInput = clientSocket.recv(4096)
            move = decodeMsg(clientInput.decode())
            while move == "BAD" or not game.makeMove(int(move[0]), int(
                    move[1])):
                #if the input was bad send the lock and garb for a retry
                sendMsgToClient(clientSocket, "1")
                time.sleep(1)
                sendMsgToClient(clientSocket, "Garb")
                clientInput = clientSocket.recv(4096)
                move = decodeMsg(clientInput.decode())
            #print the move to file
            if player_turn == 1:
                printToFile(game.getPlayer(), move, clients[0].getsockname(),
                            clients[1].getsockname())
            else:
                printToFile(game.getPlayer(), move, clients[1].getsockname(),
                            clients[0].getsockname())
            #if the move was vaild check for win codition
            #else change the player turn
            if game.checkForWin():
                sendMsgToClient(clients[0], "1")
                sendMsgToClient(clients[1], "1")
                time.sleep(1)
                if player_turn == 1:
                    sendMsgToClient(clients[0], "X won")
                    sendMsgToClient(clients[1], "X won")
                else:
                    sendMsgToClient(clients[0], "O won")
                    sendMsgToClient(clients[1], "O won")
                time.sleep(1)
                gameboard = game.toString()
                clients[0].send(gameboard.encode())
                clients[1].send(gameboard.encode())
                break
            if player_turn == 1:
                game.setPlayer(0)
            else:
                game.setPlayer(1)
    #confirm that the game has ended for both clients
    #check to see if they want to play again
    clientInput = clientSocket.recv(4096)
    if clientInput.decode() == "y":
        reset_count += 1
        while reset_count != 2:
            player_turn = player_turn
        if reset_count == 2:
            time.sleep(1)
            game.resetGame()
            sendMsgToClient(clientSocket, "y")
            reset_count = 0
            time.sleep(1)
            processClientMsg(clientSocket, player_turn)
    else:
        sendMsgToClient(clients[0], "n")
        sendMsgToClient(clients[1], "n")


#helper to decode the incoming client message to find the move to add to the board
def decodeMsg(decoded_clientMsg):
    move = ""
    if decoded_clientMsg == "A1":
        move = "00"
    elif decoded_clientMsg == "A2":
        move = "10"
    elif decoded_clientMsg == "A3":
        move = "20"
    elif decoded_clientMsg == "B1":
        move = "01"
    elif decoded_clientMsg == "B2":
        move = "11"
    elif decoded_clientMsg == "B3":
        move = "21"
    elif decoded_clientMsg == "C1":
        move = "02"
    elif decoded_clientMsg == "C2":
        move = "12"
    elif decoded_clientMsg == "C3":
        move = "22"
    else:
        move = "BAD"
    return str(move)


#helper to send clients a message
def sendMsgToClient(clientSocket, msg):
    clientSocket.send(str(msg).encode())


#prints the Player, move, IP From, IP To to file
def printToFile(player, move, ipf, ipt):
    f = open("output.txt", "a")
    f.write("Player:" + str(player) + " Move:" + str(move) + " From IP:" +
            str(ipf) + " To IP:" + str(ipt))
    f.write("\n")


#main method
if __name__ == "__main__":
    x = input("press -lh to host the game locally")
    if x == "-lh":
        hostGame('127.0.0.1', 4446)
    else:
        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname)
        hostGame(IPAddr, 4446)

