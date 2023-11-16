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

# Authors:       Brooke McWilliams
#                Morgan Miller
# Purpose:       Handle updating the client from the server
# Pre:           Client request to sync game
# Post:          Server sends update and fixes sync issues

def server_update_response(game_id: int) -> None:
    # Ensure exclusive access to the game_state data
    semaphore2.acquire()

    client1_sync = game_states[game_id][clients_sockets[0]]["sync"]
    client2_sync = game_states[game_id][clients_sockets[1]]["sync"]

    if client1_sync < client2_sync:
        game_states[game_id][clients_sockets[0]] = {
                        "playerPaddle": game_states[game_id][clients_sockets[0]]["playerPaddle"],
                        "opPaddle": game_states[game_id][clients_sockets[1]]["playerPaddle"],
                        "ball": game_states[game_id][clients_sockets[1]]["ball"],
                        "lScore": game_states[game_id][clients_sockets[1]]["lScore"],
                        "rScore": game_states[game_id][clients_sockets[1]]["rScore"],
                        "sync": game_states[game_id][clients_sockets[1]]["sync"]}
    else:
        game_states[game_id][clients_sockets[1]] = {
                        "playerPaddle": game_states[game_id][clients_sockets[1]]["playerPaddle"],
                        "opPaddle": game_states[game_id][clients_sockets[0]]["playerPaddle"],
                        "ball": game_states[game_id][clients_sockets[0]]["ball"],
                        "lScore": game_states[game_id][clients_sockets[0]]["lScore"],
                        "rScore": game_states[game_id][clients_sockets[0]]["rScore"],
                        "sync": game_states[game_id][clients_sockets[0]]["sync"]}
        game_states[game_id][clients_sockets[0]]["opPaddle"] = game_states[game_id][clients_sockets[1]]["playerPaddle"]

    # Release the semaphore
    semaphore2.release()

# ======================================================================================================================= #

# Function to handle client connection
def handle_client(client_soc: socket.socket, game_id: int) -> None:
    # Handle client update
    response = client_soc.recv(1024).decode()
    client_request = json.loads(response)

    # Ensure exclusive access to the game_state data
    semaphore.acquire()

    # Update the game based on the data sent by the client for the specific game_id
    game_states[game_id][client_soc] = client_request

    # Release the semaphore
    semaphore.release()

# ======================================================================================================================= #

# Initialize server specs
server_host = "localhost"
server_ip = 12321

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((server_host, server_ip))
server_socket.listen(5)

semaphore = threading.Semaphore(1)
semaphore2 = threading.Semaphore(1)
game_states = {}  # Dictionary to store game states for each game

connected = True

while connected:
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

    # Create a unique game_id for each pair of clients
    game_id = len(game_states)
    game_states[game_id] = {client: {} for client in clients_sockets}

    # Send the game specs to each client to start the game
    for client, specs in zip(clients_sockets, game_specs):
        client.send(json.dumps(specs).encode())

    # Handle each client in a separate thread
    threads = [threading.Thread(target=handle_client, args=(client, game_id)) for client in clients_sockets]

    # Handle server response
    server_update_response(game_id)

    # Send the update to the clients
    for client in clients_sockets:
        client.send(json.dumps(game_states[game_id][client]).encode())

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

# # Close the client sockets
# for socket in clients_sockets:
#     socket.close()

# # Close the server socket when done
# server_socket.close()


