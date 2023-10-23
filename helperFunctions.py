# ============================================ Heading ============================================ #

# Contributing Authors:     Brooke McWilliams
# Email Addresses:          brmc230@uky.edu
# Date:                     Created: 10/23/2023
#                           Last Edited: 10/23/2023 
# Purpose:                  A file containing helper functions/methods to reduce redundancy in the code
#                           These are student implemented functions/methods                             

# ============================================ Template ============================================ #

# Author:       <Who wrote this method> 
# Purpose:      <What should this method do> 
# Pre:          <What preconditions does this method expect to be true? Ex. This method 
#               expects the program to be in X state before being called> 
# Post:         <What postconditions are true after this method is called? Ex. This method 
#               changed global variable X to Y>

# ================================================================================================== #
import socket
from assets.code.helperCode import *

# Author:       Brooke McWilliams
# Purpose:      Client updates the server on paddle information, ball location, and the
#               current score of the game
# Pre:          When this method is called the game is expected to be finished updating the
#               clients individual information 
# Post:         This method sends to the server the clients information

def update_server(paddleInfo:Paddle, ballInfo:Ball, scoreL:int, scoreR:int, client:socket.socket) -> None:
    try: 
        client_information = f"playerPaddle: {paddleInfo}, ball: {ballInfo}, lScore: {scoreL}, rScore: {scoreR}"
        client.send(client_information.encode())

    except Exception as e:
        print(f"Error: {e}")
