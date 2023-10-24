# ======================================================================================================================= #
# Contributing Authors:	    Brooke McWilliams
#                           
# Email Addresses:          brmc230@uky.edu
#                        
# Date:                     10/23/2023
# Purpose:                  Code that implements the server side of the Pong game and interacts with
#                           the client
# Misc:                     
# ======================================================================================================================= #
import json
import socket
import threading
import pyautogui

# Use this file to write your server logic
# You will need to support at least two clients
# You will need to keep track of where on the screen (x,y coordinates) each paddle is, the score 
#   for each player and where the ball is, and relay that to each client
# I suggest you use the sync variable in pongClient.py to determine how out of sync your two
#   clients are and take actions to resync the games
# Make precautions for if someone enters the wrong IP or port and if a 3rd person attempts to 
#   connect to an already full game

# ======================================================================================================================= #
# Author:       Brooke McWilliams
# Purpose:      Handle client connection
# Pre:          This function carries out the instructions for the client
# Post:         Sends the client the information it was asking for

def handle_client(client_ID:str) -> None: 
    client = client_sockets_dict[client_ID]

    try:
        while True: 
            response = client.recv(1024).decode()
            # Client disconnected
            if not response:
                break

            # Ensure exclusive access with the semaphore
            semaphore.acquire()
            try:
                client_request = json.loads(response)

                # Update game state conditions here and call appropriate functions
                if client_request == "join_server":
                    join_server_response(client_sockets_dict[client_ID])



                # Update the other client 
                for clients in client_sockets_dict:
                    if clients != client_ID:
                        client_sockets_dict[clients].send(json.dumps(game_state).encode())

            except Exception as e:
                print(f"Error processing client request: {str(e)}")
            finally:
                # Release the semaphore to allow access to other threads
                semaphore.release()

    except Exception as e:
        print(f"Client connection error: {str(e)}")
    finally:
        del client_sockets_dict[client_ID]
        client_socket.close()

# ======================================================================================================================= #
# Author:       Brooke McWilliams
# Purpose:      Handle if the client request to join the server
# Pre:          Client runs the joinServer function
# Post:         Server sends corresponding information back to client

def join_server_response(client_soc:socket.socket) -> None:
    join_server_response_data = {   "screen_width": 1920,
                                    "screen_height": 1080,
                                    "player_paddle": game_state[client_ID]["paddle"] }
# Don't know what to send here because I don't yet know how to receieve it or what im actually sending?
    client_soc.send(json.dumps(join_server_response_data).encode())





# ======================================================================================================================= #

# Initialize the server specs, don't know if this is 100% correct yet
server_host = "localhost"
server_ip = 12321

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # For local host use
server_socket.bind((server_host, server_ip))

# Listen for clients
server_socket.listen(5)


semaphore = threading.Semaphore()
client_sockets_dict = dict()
first_client = False
game_state = dict()
connected_players = 0

while connected_players < 2:
    # Accept connection from the client
    client_socket, client_ip = server_socket.accept() 
    # Give the client a unique ID to reference and add to the clients dictionary
    client_ID = f"client_{client_ip[0]}_{client_ip[1]}"
    client_sockets_dict[client_ID] = client_socket

    game_state = {key: {} for key in client_sockets_dict.keys()}

    if not first_client:
        game_state[client_ID]["paddle"] = "right"
        first_client = True
    else:
        game_state[client_ID]["paddle"] = "left"

# Handle the clients with threads
handle_client = threading.Thread(target=handle_client, args=(client_ID,))
handle_client.start()

