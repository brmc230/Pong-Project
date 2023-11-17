# Contributing Authors:	    Brooke McWilliams
#                           Morgan Miller
# Email Addresses:          brmc230@uky.edu
#                           mdmi240@uky.edu
# Date:                     10/23/2023
#                           11/17/2023
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

def server_update(client_soc:socket.socket) -> None:
        # Receive the clients message and decode it so that the server can read it properly 
        response = client_soc.recv(1024).decode()
        client_request = json.loads(response)

        # Ensure exclusive access to the game_state data
        semaphore.acquire()

        # Update the game state dictionary based on the the data sent by the client
        game_state[client_soc] = client_request

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

    # Update the first clients game state dictionary if it is behind of the second clients sync variable
    # The first client is used as a "default game state" in order to keep both clients games in sync so
    #   if the first client is up to date, the second client is updated with the first clients game state
    #   dictionary of where the ball is and the first clients paddle etc but the player paddle is left untouched
    if game_state[clients_sockets[0]]["sync"] < game_state[clients_sockets[1]]["sync"]:
        game_state[clients_sockets[0]] = { 
                        "playerPaddle": game_state[clients_sockets[0]]["playerPaddle"],
                        "opPaddle": game_state[clients_sockets[1]]["playerPaddle"],
                        "ball": game_state[clients_sockets[1]]["ball"], 
                        "lScore": game_state[clients_sockets[1]]["lScore"],
                        "rScore": game_state[clients_sockets[1]]["rScore"],
                        "sync": game_state[clients_sockets[1]]["sync"] }
    else:
        game_state[clients_sockets[1]] = { 
                        "playerPaddle": game_state[clients_sockets[1]]["playerPaddle"],
                        "opPaddle": game_state[clients_sockets[0]]["playerPaddle"],
                        "ball": game_state[clients_sockets[0]]["ball"],
                        "lScore": game_state[clients_sockets[0]]["lScore"],
                        "rScore": game_state[clients_sockets[0]]["rScore"],
                        "sync": game_state[clients_sockets[0]]["sync"] }
        # Remember that one clients playerPaddle is another clients opPaddle
        game_state[clients_sockets[0]]["opPaddle"] = game_state[clients_sockets[1]]["playerPaddle"]

    # Release the semaphore
    semaphore2.release()

# ======================================================================================================================= #

# Initialize the server specs
server_host = "localhost" # 10.47.137.190
server_ip = 12321

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((server_host, server_ip))

# Listen for clients
server_socket.listen(5)

# Create the semaphores to ensure that the clients do not have a race to the game state dictionary
# Create the lists to hold each client connection and the game specs to send to fire the game up on
#   the clients side
semaphore = threading.Semaphore(1)
semaphore2 = threading.Semaphore(1)
clients_sockets = list()
game_specs = list()

# Establish connections with clients 
while len(clients_sockets) < 2:
    # Game metrics that set the paddle for each client
    client_game_metrics = {"screen_width": 800,
                            "screen_height": 600,
                            "player_paddle": ("left" if len(clients_sockets) == 0 else "right")}
    game_specs.append(client_game_metrics)
    
    # Accept the client connection and add the new client to the list
    client_socket, client_ip = server_socket.accept()
    clients_sockets.append(client_socket)

# Send the game specs to the clients to fire the game up
clients_sockets[0].send(json.dumps(game_specs[0]).encode())
clients_sockets[1].send(json.dumps(game_specs[1]).encode())


# Create the game state dictionary for each client
# Ensure that the initial game state is properly set between the two clients when you start the game
game_state = {value: {"playerPaddle": [0, 0, ""], "opPaddle": [0, 0, ""], "ball": [0, 0], "lScore": 0, "rScore": 0, "sync": 0} for value in clients_sockets}

connected = True
# Handle the clients in threads to loop  through the game state until the game is over
while connected:
    # Run the server update function in threads with a semaphore to ensure each clients message to the server
    #   is properly handled and the clients do not "race" to update the game state dictionary 
    threads = []
    for socke in clients_sockets:
        client = threading.Thread(target=server_update, args=(socke,))
        threads.append(client)

    threads[0].start(), threads[1].start()
    threads[0].join(), threads[1].join()

    # Have the server compare each clients dictionary and update the game state accordingly 
    server_update_response()

    # Send the updated game states to each client
    clients_sockets[0].send(json.dumps(game_state[clients_sockets[0]]).encode()) 
    clients_sockets[1].send(json.dumps(game_state[clients_sockets[1]]).encode())


# Close the client sockets 
for socke in clients_sockets:
    socke.close()

# Close the server socket 
server_socket.close()