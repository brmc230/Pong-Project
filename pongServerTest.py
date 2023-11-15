# ======================================================================================================================= #
# Contributing Authors:	   Morgan Miller, Brooke McWilliams
#                           
# Email Addresses:          mdmi240@uky.edu, brmc230@uky.edu
#                        
# Date:                     11/08/2023
# Purpose:                  Code that implements the server side of the Pong game and interacts with
#                           the client
# Misc:                     
# ======================================================================================================================= #
import json
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

# ======================================================================================================================= #
# Author:       Morgan Miller
# Purpose:      Game state to keep track of each client's game data
# Pre:          It is the initial setup of the game_state dictionary and the semaphore object
# Post:         After the execution of this statement, the game_state dictionary is initialized and the semaphore object is initialized with an initial value of 1

# Game state to keep track of each client's game data
game_state = {}
semaphore = threading.Semaphore(1)

# Author:       Brooke McWilliams, Morgan Miller
# Purpose:       Function to handle individual clients
# Pre:          This function carries out the instructions for the client
# Post:         Sends the client the information it was asking for

def handle_client(client_soc, client_id):
    global game_state
    connected = True
    try:
        while connected:
            data = client_soc.recv(1024).decode()
            if not data:
                connected = False
                break
            client_request = json.loads(data)
            try:
                semaphore.acquire()
                update_game_state(client_id, client_request)
                server_update_response(game_state, client_id, client_soc)
            except Exception as e:
                print(f"Error processing client request: {str(e)}")
            semaphore.release()
    except Exception as e:
        print(f"Client connection error: {str(e)}")
    finally:
        client_soc.close()

# Author:        Morgan Miller
# Purpose:       Function to update the game state based on client data
# Pre:           The game_state dictionary is accessible and contains an entry for the specified client_id, and the data parameter holds the game data provided by the client.
# Post:          The function updates the game data for the specific client, identified by the client_id parameter, in the game_state dictionary based on the information provided in the data parameter

def update_game_state(client_id, data):
    global game_state
    if client_id in game_state:
        game_state[client_id].update(data)


# Author:        Brooke McWilliams, Morgan Miller
# Purpose:       Function to send game state updates to clients
# Pre:           The game_state dictionary is accessible and contains game data for each client, and the client_id parameter identifies the specific client for which the response is being generated.
# Post:          The function sends the updated game state data from the game_state dictionary to all clients except the one identified by the client_id parameter via the client_soc socket.

def server_update_response(game_state, client_id, client_soc):
    for key in game_state:
        if key != client_id:
            response_data = game_state[key]
            client_soc.send(json.dumps(response_data).encode())

# Initialize the server socket
server_host = "localhost"
server_port = 12321

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((server_host, server_port))
server_socket.listen(5)

connected_players = 0

while connected_players < 2:
    client_soc, client_addr = server_socket.accept()
    client_id = f"client_{client_addr[0]}_{client_addr[1]}"
    game_state[client_id] = {}
    connected_players += 1
    if connected_players == 2:
        break

# Start threads for handling each client
threads = []
for key in game_state:
    thread = threading.Thread(target=handle_client, args=(client_soc, key))
    threads.append(thread)
    thread.start()

# Join all threads
for thread in threads:
    thread.join()

# Close the server socket
server_socket.close()
