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
import time

# ======================================================================================================================= #
# Authors:      Brooke McWilliams
#               Morgan Miller
# Purpose:      Handle client connection
# Pre:          This function carries out the instructions for the client
# Post:         Sends the client the information it was asking for

def server_update(client_soc:socket.socket) -> None:
        response = client_soc.recv(1024).decode()
        client_request = json.loads(response)

        # Ensure exclusive access to the game_state data
        semaphore.acquire()

        # Update the game based on the the data sent by the client
        game_state[client_soc].update(client_request)

        # Release the semaphore
        semaphore.release()

# ======================================================================================================================= #

# Authors:       Brooke McWilliams
#                Morgan Miller
# Purpose:       Handle updating the client from the server
# Pre:           Client request to sync game
# Post:          Server sends update and fixes sync issues

def server_update_response() -> None:
    # Ensure exclusive access to the game_state data
    semaphore2.acquire()

    if game_state[clients_sockets[0]]["sync"] > game_state[clients_sockets[1]]["sync"]:
        game_state[clients_sockets[1]].update({ "opPaddle": game_state[clients_sockets[0]]["playerPaddle"],
                                    "ball": game_state[clients_sockets[0]]["ball"],
                                    "lScore": game_state[clients_sockets[0]]["lScore"],
                                    "rScore": game_state[clients_sockets[0]]["rScore"],
                                    "sync": game_state[clients_sockets[0]]["sync"]})

    elif game_state[clients_sockets[0]]["sync"] < game_state[clients_sockets[1]]["sync"]:
        game_state[clients_sockets[0]].update({ "opPaddle": game_state[clients_sockets[1]]["playerPaddle"],
                                        "ball": game_state[clients_sockets[1]]["ball"], 
                                        "lScore": game_state[clients_sockets[1]]["lScore"],
                                        "rScore": game_state[clients_sockets[1]]["rScore"],
                                        "sync": game_state[clients_sockets[1]]["sync"]})
                
    # Release the semaphore
    semaphore2.release()

# ======================================================================================================================= #

# Initialize the server specs, don't know if this is 100% correct yet
server_host = "127.0.0.1" # 10.47.171.218
server_ip = 5555 # 9010

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # For local host use
server_socket.bind((server_host, server_ip))

# Listen for clients
server_socket.listen(5)

semaphore = threading.Semaphore(1)
semaphore2 = threading.Semaphore(1)
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
clients_sockets[0].send(json.dumps(game_specs[0]).encode())
clients_sockets[1].send(json.dumps(game_specs[1]).encode())


# Create the game state dictionary for each client
game_state = {value: {} for value in clients_sockets}

connected = True

# Handle the clients in threads to loop  through the game state until the game is over
while connected is True:

    threads = []
    for socke in clients_sockets:
        client = threading.Thread(target=server_update, args=(socke,))
        threads.append(client)

    threads[0].start(), threads[1].start()
    threads[0].join(), threads[1].join()

    threads = []
    for socke in clients_sockets:
        client = threading.Thread(target=server_update_response)
        threads.append(client)
    
    threads[0].start(), threads[1].start()
    threads[0].join(), threads[1].join()

    # Send the updated game states to each client
    client0 = json.dumps(game_state[clients_sockets[0]])
    client1 = json.dumps(game_state[clients_sockets[1]])

    clients_sockets[0].send(client0.encode()) 
    clients_sockets[1].send(client1.encode())


# # Close the client sockets 
# for socke in clients_sockets:
#     socke.close()

# # Close the server socket when done 
# server_socket.close()

