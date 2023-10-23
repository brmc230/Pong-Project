# =================================================================================================
# Contributing Authors:	    Brooke McWilliams
#                           
# Email Addresses:          brmc230@uky.edu
#                        
# Date:                     10/23/2023
# Purpose:                  Code that implements the server side of the Pong game and interacts with
#                           the client
# Misc:                     
# =================================================================================================

from helperFunctions import *
from pongClient import *
import socket
import threading

# Use this file to write your server logic
# You will need to support at least two clients
# You will need to keep track of where on the screen (x,y coordinates) each paddle is, the score 
#   for each player and where the ball is, and relay that to each client
# I suggest you use the sync variable in pongClient.py to determine how out of sync your two
#   clients are and take actions to resync the games
# Make precautions for if someone enters the wrong IP or port and if a 3rd person attempts to 
#   connect to an already full game

# Initialize the server specs, don't know if this is 100% correct yet
server_host = "localhost"
server_ip = 12321

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # For local host use
server_socket.bind((server_host, server_ip))

# Listen for clients
server_socket.listen(5)

# Getting client information
semaphore = threading.Semaphore()
connected_clients = 0
minimum_clients = 2
client_sockets = []

while connected_clients < minimum_clients:
    client_socket, client_ip = server_socket.accept()

    # Handle the clients with threads
    handle_client = threading.Thread(target=handle_client, args=(client_socket,))
    handle_client.start()
