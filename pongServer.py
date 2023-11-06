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

def handle_client(client_soc:socket.socket, client:str) -> None: 
    global semaphore
    global client_sockets_dict
    global server_socket
    connected = True
    try:
        while connected: 
            server_socket.listen(5)
            response = client_soc.recv(1024).decode()
            # # Client disconnected
            # if not response:
            #     connected = False
            #     break

            client_request = json.loads(response)

            try:
                # Ensure exclusive access with the semaphore
                semaphore.acquire()

                # Update game state conditions here and call appropriate functions
                if "codeword" in client_request:
                    client_request = json.loads(response)
                    update_client_data(client, client_request)
                elif "server_update" in client_request:
                    server_update_response(client_sockets_dict, client, client_soc)
                elif "game_over" in client_request:
                    connected = False 
            
                # # Update other clients values
                # for key, value in client_sockets_dict.items():
                #     if value != client_soc:
                #         client_sockets_dict[key].send(json.dumps(game_state).encode())

            except Exception as e:
                print(f"Error processing client request: {str(e)}")

            # Release the semaphore to allow access to other threads
            semaphore.release()

    except Exception as e:
        print(f"Client connection error: {str(e)}")

# ======================================================================================================================= #
# Author:       Brooke McWilliams
# Purpose:      Handle if the client request to join the server
# Pre:          Client runs the joinServer function
# Post:         Server sends corresponding information back to client

def join_server_response(client_soc:socket.socket, client:str) -> None:
    global game_state
    join_server_response_data = {"screen_width": 800,
                                    "screen_height": 600,
                                    "player_paddle": game_state[client]["paddle"]}
    client_soc.send(json.dumps(join_server_response_data).encode())

# ======================================================================================================================= #

# Author:       Brooke McWilliams
# Purpose:      Handle if the client sends thier game data
# Pre:          Client sends an update of their data
# Post:         Server updates corresponding values for the client

def update_client_data(client_id:str, data:dict) -> None:
    global game_state
    for key, value in data.items():
        if key == "playerPaddle":
            game_state[client_id]["paddle_loc"] = value
        elif key == "opPaddle":
            game_state[client_id]["paddle_locOP"] = value
        elif key == "ball":
            game_state[client_id]["ball_loc"] = value
        elif key == "lScore":
            game_state[client_id]["lScore"] = value
        elif key == "rScore":
            game_state[client_id]["rScore"] = value
        elif key == "sync":
            game_state[client_id]["sync"] = value
        
# ======================================================================================================================= #

# Author:       Brooke McWilliams
# Purpose:      Handle updating the client from the server
# Pre:          Client request to sync with other client
# Post:         Server sends update and fixes sync issues

def server_update_response(clients:dict, clientid:str, clientSoc:socket.socket) -> None:
    global game_state
    for key in clients:
        if key != clientid:
            opponent_subdict = clients[key]
            opp_key = key
            for subkey, value in opponent_subdict.items():
                if subkey == "sync":
                    if value > game_state[clientid][subkey]:
                        game_state[clientid]["paddle_locOP"] = game_state[opp_key]["paddle_loc"]
                        game_state[clientid]["ball"] = game_state[opp_key]["ball"]
                        game_state[clientid]["lScore"] = game_state[opp_key]["lScore"]
                        game_state[clientid]["rScore"] = game_state[opp_key]["rScore"]
                        game_state[clientid]["sync"] = game_state[opp_key]["sync"]
                    elif value < game_state[clientid][subkey]:
                        game_state[opp_key]["paddle_locOP"] = game_state[clientid]["paddle_loc"]
                        game_state[opp_key]["ball"] = game_state[clientid]["ball"]
                        game_state[opp_key]["lScore"] = game_state[clientid]["lScore"]
                        game_state[opp_key]["rScore"] = game_state[clientid]["rScore"]
                        game_state[opp_key]["sync"] = game_state[clientid]["sync"]
            
    clientSoc.send(json.dumps(game_state[clientid]).encode())

# ======================================================================================================================= #

# Initialize the server specs, don't know if this is 100% correct yet
server_host = "localhost"
server_ip = 12321

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # For local host use
server_socket.bind((server_host, server_ip))

# Listen for clients
server_socket.listen(5)

semaphore = threading.Semaphore(1)
connected_players = 0
game_over = False
first_client = True
client_sockets_dict = dict()
game_state = dict()

while connected_players < 1:
    # Accept connection from the client
    client_socket, client_ip = server_socket.accept() 
    # Give the client a unique ID to reference and add to the clients dictionary
    client_ID = f"client_{client_ip[0]}_{client_ip[1]}"
    client_sockets_dict[client_ID] = client_socket
    connected_players += 1

# Create the game state dict to keep track of the game for each client
game_state = {key: {} for key in client_sockets_dict.keys()}


for key in client_sockets_dict.keys():
    if first_client is True:
        game_state[key]["paddle"] = "right"
        game_state[key]["paddle_loc"] = []
        game_state[key]["paddle_locOP"] = []
        game_state[key]["ball_loc"]= []
        game_state[key]["rScore"] = 0
        game_state[key]["lScore"] = 0
        game_state[key]["sync"] = 0
        first_client = False
    else:
        game_state[key]["paddle"] = "left"
        game_state[key]["paddle_loc"] = []
        game_state[key]["paddle_locOP"] = []
        game_state[key]["ball_loc"]= []
        game_state[key]["rScore"] = 0
        game_state[key]["lScore"] = 0
        game_state[key]["sync"] = 0

# Get specs for the joinServer function to relay back to client
for key, value in client_sockets_dict.items():
    join_server_response(value, key)

# Handle the clients with threads
i = 0
for key, value in client_sockets_dict.items():
    if i == 0:
        client_one = threading.Thread(target=handle_client, args=(value, key,))
    # else:
    #     client_two = threading.Thread(target=handle_client, args=(value, key, semaphore ))
    # i = 1

threads = [client_one]

for thread in threads:
    thread.start()

for thread in threads:
    thread.join()

for value in client_sockets_dict.values():
    value.close()

server_socket.close()


