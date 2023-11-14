# Contributing Authors:	    Brooke McWilliams
#                           Morgan Miller
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

# ======================================================================================================================= #
# Authors:      Brooke McWilliams
#               Morgan Miller
# Purpose:      Handle client connection
# Pre:          This function carries out the instructions for the client
# Post:         Sends the client the information it was asking for

def handle_client(client_soc:socket.socket) -> None:
    connected = True

    while connected:
        server_socket.listen(5)
        response = client_soc.recv(1024).decode()
        client_request = json.loads(response)

        # Ensure exclusive access to the game_state data
        semaphore.acquire()
        game_state[client_soc].update(client_request)
        # Release the semaphore
        semaphore.release()

        # Handle when somebody wins/loses
        if client_request["gameOver"] is True:
            connected = False

        # Update the game state conditions
        server_update_response(client_soc)

# ======================================================================================================================= #

# Authors:       Brooke McWilliams
#                Morgan Miller
# Purpose:       Handle updating the client from the server
# Pre:           Client request to sync game
# Post:          Server sends update and fixes sync issues

def server_update_response(client_soc:socket.socket) -> None:
    for client in clients_sockets:
        if client != client_soc:
            if game_state[client_soc]["sync"] > game_state[client]["sync"]:
                game_state[client].update({ "opPaddle": game_state[client_soc]["playerPaddle"],
                                            "ball": game_state[client_soc]["ball"],
                                            "lScore": game_state[client_soc]["lScore"],
                                            "rScore": game_state[client_soc]["rScore"],
                                            "sync": game_state[client_soc]["sync"]})
                client.send(json.dumps(game_state[client]).encode())
            elif game_state[client_soc]["sync"] < game_state[client]["sync"]:
                game_state[client_soc].update({ "opPaddle": game_state[client]["playerPaddle"],
                                                "ball": game_state[client]["ball"], 
                                                "lScore": game_state[client]["lScore"],
                                                "rScore": game_state[client]["rScore"],
                                                "sync": game_state[client]["sync"]})
                client_soc.send(json.dumps(game_state[client_soc]).encode())

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
clients_sockets = list()
game_specs = list()

# Establish connections with clients 
while len(clients_sockets) < 2:
    # Game metrics 
    client_game_metrics = {"screen_width": 800,
                            "screen_height": 600,
                            "player_paddle": ("left" if len(clients_sockets) == 0 else "right")}
    game_specs.append(client_game_metrics)
    
    client_socket, client_ip = server_socket.accept()
    clients_sockets.append(client_socket)

# Send the game specs to the client to fire the game up
i = 0
for i in range(len(clients_sockets)):
    clients_sockets[i].send(json.dumps(game_specs[i]).encode())
    i += 1
    
# Create the game state dictionary for each client
game_state = {value: {} for value in clients_sockets}

# Handle the clients in threads 
threads = []
for socke in clients_sockets:
    client = threading.Thread(target=handle_client, args=(socke,))
    threads.append(client)

threads[0].start(), threads[1].start()

for thread in threads:
    thread.join()

for socke in clients_sockets:
    socke.close()

# Close the server socket when done 
server_socket.close()

