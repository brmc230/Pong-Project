# ======================================================= Heading ======================================================== #

# Contributing Authors:     Brooke McWilliams
# Email Addresses:          brmc230@uky.edu
# Date:                     Created: 10/23/2023
#                           Last Edited: 10/23/2023 
# Purpose:                  A file containing helper functions/methods to reduce redundancy in the code
#                           These are student implemented functions/methods                             

# ======================================================= Template ======================================================= #

# Author:       <Who wrote this method> 
# Purpose:      <What should this method do> 
# Pre:          <What preconditions does this method expect to be true? Ex. This method 
#               expects the program to be in X state before being called> 
# Post:         <What postconditions are true after this method is called? Ex. This method 
#               changed global variable X to Y>

# ======================================================================================================================= #
from assets.code.helperCode import *
from pongServer import *
import socket
import threading
# ======================================================================================================================= #

# Author:       Brooke McWilliams
# Purpose:      Client updates the server on paddle information, ball location, and the
#               current score of the game
# Pre:          When this function is called the game is expected to be finished updating the
#               clients individual information 
# Post:         This function sends to the server the clients information

def update_server(paddleInfo:Paddle, ballInfo:Ball, scoreL:int, scoreR:int, client:socket.socket) -> None:
    try: 
        client_information = f"playerPaddle: {paddleInfo}, ball: {ballInfo}, lScore: {scoreL}, rScore: {scoreR}"
        client.send(client_information.encode())

    except Exception as e:
        print(f"Error: {e}")

# ======================================================================================================================= #

# Author:       Brooke McWilliams
# Purpose:      Handle client connection
# Pre:          This function sets up individual clients with semaphores 
# Post:         Adds clients to the client list and handles client information

def handle_client(client_socket:socket.socket) -> None: 
    with semaphore:
        connected_clients += 1
        client_sockets.append(client_socket)
    
    while True: 
        client_data = client_socket.recv(1024)

        # Client disconnected
        if not client_data:
            with semaphore:
                connected_clients -= 1
                client_sockets.remove(client_socket)
            client_socket.close()
            break

        # Update game state conditions here
        game_state = dict()

        for client in client_sockets:
            client.send(game_state)