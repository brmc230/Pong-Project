# =================================================================================================
# Contributing Authors:	    Brooke McWilliams
#                           
#
# Email Addresses:          brmc230@uky.edu
#
#                           
# Date:                     10/22/2023
#
# Purpose:                  Code that implements the server side of the Pong game and interacts with
#                           the client
#
# Misc:                     <Not Required.  Anything else you might want to include>
# =================================================================================================

import socket
import threading

# Use this file to write your server logic
# You will need to support at least two clients
# You will need to keep track of where on the screen (x,y coordinates) each paddle is, the score 
#   for each player and where the ball is, and relay that to each client
# I suggest you use the sync variable in pongClient.py to determine how out of sync your two
#   clients are and take actions to resync the games

# Make precautions for if someone enters the wrong IP or port and if a 3rd person attempts to connect to an already full game
