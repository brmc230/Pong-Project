# ======================================================================================================================= #
# Contributing Authors:	    Brooke McWilliams
                            Morgan Miller
# Email Addresses:          brmc230@uky.edu
                            mdmi240@uky.edu
# Date:                     10/23/2023
# Purpose:                  This file implements the client side of the pong game in connection to
#                           the server
# Misc:                     
# ======================================================================================================================= #

import pygame
import tkinter as tk
import sys
import socket
import json
from assets.code.helperCode import *


# This is the main game loop.  For the most part, you will not need to modify this.  The sections
# where you should add to the code are marked.  Feel free to change any part of this project
# to suit your needs.
def playGame(screenWidth:int, screenHeight:int, playerPaddle:str, client:socket.socket) -> None:
    
    # Pygame inits
    pygame.mixer.pre_init(44100, -16, 2, 2048)
    pygame.init()

    # Constants
    WHITE = (255,255,255)
    clock = pygame.time.Clock()
    scoreFont = pygame.font.Font("./assets/fonts/pong-score.ttf", 32)
    winFont = pygame.font.Font("./assets/fonts/visitor.ttf", 48)
    pointSound = pygame.mixer.Sound("./assets/sounds/point.wav")
    bounceSound = pygame.mixer.Sound("./assets/sounds/bounce.wav")

    # Display objects
    screen = pygame.display.set_mode((screenWidth, screenHeight))
    topWall = pygame.Rect(-10,0,screenWidth+20, 10)
    bottomWall = pygame.Rect(-10, screenHeight-10, screenWidth+20, 10)
    centerLine = []
    for i in range(0, screenHeight, 10):
        centerLine.append(pygame.Rect((screenWidth/2)-5,i,5,5))

    # Paddle properties and init
    paddleHeight = 50
    paddleWidth = 10
    paddleStartPosY = (screenHeight/2)-(paddleHeight/2)
    leftPaddle = Paddle(pygame.Rect(10,paddleStartPosY, paddleWidth, paddleHeight))
    rightPaddle = Paddle(pygame.Rect(screenWidth-20, paddleStartPosY, paddleWidth, paddleHeight))

    ball = Ball(pygame.Rect(screenWidth/2, screenHeight/2, 5, 5), -5, 0)

    playerPaddleObj = leftPaddle if playerPaddle == "left" else rightPaddle
    opponentPaddleObj = rightPaddle if playerPaddle == "left" else leftPaddle

    lScore = 0
    rScore = 0
    game_over = False

    sync = 0

    while True:
        # Wiping the screen
        screen.fill((0,0,0))

        # Getting keypress events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    playerPaddleObj.moving = "down"
                elif event.key == pygame.K_UP:
                    playerPaddleObj.moving = "up"
            elif event.type == pygame.KEYUP:
                playerPaddleObj.moving = ""

        # Update the player paddle and opponent paddle's location on the screen
        for paddle in [playerPaddleObj, opponentPaddleObj]:
            if paddle.moving == "down":
                if paddle.rect.bottomleft[1] < screenHeight-10:
                    paddle.rect.y += paddle.speed
            elif paddle.moving == "up":
                if paddle.rect.topleft[1] > 10:
                    paddle.rect.y -= paddle.speed

        # If the game is over, display the win message
        if lScore > 4 or rScore > 4:
            winText = "Player 1 Wins! " if lScore > 4 else "Player 2 Wins! "
            textSurface = winFont.render(winText, False, WHITE, (0,0,0))
            textRect = textSurface.get_rect()
            textRect.center = ((screenWidth/2), screenHeight/2)
            screen.blit(textSurface, textRect)
            game_over = True
        # ==== Ball Logic =====================================================================
        ball.updatePos()

        # If the ball makes it past the edge of the screen, update score, etc.
        if ball.rect.x > screenWidth:
            lScore += 1
            pointSound.play()
            ball.reset(nowGoing="left")
        elif ball.rect.x < 0:
            rScore += 1
            pointSound.play()
            ball.reset(nowGoing="right")
            
        # If the ball hits a paddle
        if ball.rect.colliderect(playerPaddleObj.rect):
            bounceSound.play()
            ball.hitPaddle(playerPaddleObj.rect.center[1])
        elif ball.rect.colliderect(opponentPaddleObj.rect):
            bounceSound.play()
            ball.hitPaddle(opponentPaddleObj.rect.center[1])
            
        # If the ball hits a wall
        if ball.rect.colliderect(topWall) or ball.rect.colliderect(bottomWall):
            bounceSound.play()
            ball.hitWall()
        
        pygame.draw.rect(screen, WHITE, ball)
        # ==== End Ball Logic =================================================================

        # Drawing the dotted line in the center
        for i in centerLine:
            pygame.draw.rect(screen, WHITE, i)
        
        # Drawing the player's new location
        for paddle in [playerPaddleObj, opponentPaddleObj]:
            pygame.draw.rect(screen, WHITE, paddle)

        pygame.draw.rect(screen, WHITE, topWall)
        pygame.draw.rect(screen, WHITE, bottomWall)
        updateScore(lScore, rScore, screen, WHITE, scoreFont)
        pygame.display.update()
        clock.tick(60)
        
        # This number should be synchronized between you and your opponent.  If your number is larger
        # then you are ahead of them in time, if theirs is larger, they are ahead of you, and you need to
        # catch up (use their info)
        sync += 1

        # Your code here to send an update to the server on your paddle's information,
        # where the ball is and the current score.
        # Feel free to change when the score is updated to suit your needs/requirements
        client_paddle = [playerPaddleObj.rect.x, playerPaddleObj.rect.y]
        oppo_paddle = [opponentPaddleObj.rect.x, opponentPaddleObj.rect.y]
        shared_ball = [ball.rect.x, ball.rect.y]

        client_game_data = {    "playerPaddle": client_paddle,
                                "opPaddle" : oppo_paddle,
                                "ball": shared_ball,
                                "lScore": lScore,
                                "rScore": rScore,
                                "gameOver": game_over,
                                #the server response now includes the correct sync value
                                # "sync": sync 
                           } 
        client.send(json.dumps(client_game_data).encode())  

        # =========================================================================================
        # Send your server update here at the end of the game loop to sync your game with your
        #  opponent's game 
        # Whoever is behind needs to be updated to reflect correct balls position
        # Same logic with paddles
        response = client.recv(1024).decode()
        server_response = json.loads(response)
        
        # Update game state with server response
        playerPaddleObj.rect.x, playerPaddleObj.rect.y = server_response["playerPaddle"][0], server_response["playerPaddle"][1]
        opponentPaddleObj.rect.x, opponentPaddleObj.rect.y = server_response["opPaddle"][0], server_response["opPaddle"][1]


         ball.rect.x, ball.rect.y = server_response["ball"][0], server_response["ball"][1]

        lScore, rScore = server_response["lScore"], server_response["rScore"]

        # sync is updated based on server response
        sync = server_response["sync"]

        # =========================================================================================

# This is where you will connect to the server to get the info required to call the game loop.  Mainly
# the screen width, height and player paddle (either "left" or "right")
# If you want to hard code the screen's dimensions into the code, that's fine, but you will need to know
# which client is which
def joinServer(ip:str, port:str, errorLabel:tk.Label, app:tk.Tk) -> None:
    # Purpose:      This method is fired when the join button is clicked
    # Arguments:
    # ip            A string holding the IP address of the server
    # port          A string holding the port the server is using
    # errorLabel    A tk label widget, modify it's text to display messages to the user (example below)
    # app           The tk window object, needed to kill the window
    
    # Create a socket and connect to the server
    # You don't have to use SOCK_STREAM, use what you think is best
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((ip, int(port)))
    # # Get the required information from your server (screen width, height & player paddle, "left or "right)

    # Display that the game is waiting for the second player to join
    errorLabel.config(text="Waiting for another player to join . . .")
    errorLabel.update()
    # Receive the server response and collect the playGame data
    response = client.recv(1024).decode()
    join_server_data = json.loads(response)

    screenWidth = join_server_data["screen_width"]
    screenHeight = join_server_data["screen_height"]
    playerPaddle = join_server_data["player_paddle"]

    # If you have messages you'd like to show the user use the errorLabel widget like so
    errorLabel.config(text=f"Connection Accepted. Your input: IP: {ip}, Port: {port}")
    # You may or may not need to call this, depending on how many times you update the label
    errorLabel.update() 
   
    # Close this window and start the game with the info passed to you from the server
    app.withdraw()     # Hides the window (we'll kill it later)
    playGame(screenWidth, screenHeight, playerPaddle, client)  # User will be either left or right paddle ("left"|"right")
    app.quit()         # Kills the window


# This displays the opening screen, you don't need to edit this (but may if you like)
def startScreen():
    app = tk.Tk()
    app.title("Server Info")

    image = tk.PhotoImage(file="./assets/images/logo.png")

    titleLabel = tk.Label(image=image)
    titleLabel.grid(column=0, row=0, columnspan=2)

    ipLabel = tk.Label(text="Server IP:")
    ipLabel.grid(column=0, row=1, sticky="W", padx=8)

    ipEntry = tk.Entry(app)
    ipEntry.grid(column=1, row=1)

    portLabel = tk.Label(text="Server Port:")
    portLabel.grid(column=0, row=2, sticky="W", padx=8)

    portEntry = tk.Entry(app)
    portEntry.grid(column=1, row=2)

    errorLabel = tk.Label(text="")
    errorLabel.grid(column=0, row=4, columnspan=2)

    joinButton = tk.Button(text="Join", command=lambda: joinServer(ipEntry.get(), portEntry.get(), errorLabel, app))
    joinButton.grid(column=0, row=3, columnspan=2)

    app.mainloop()

if __name__ == "__main__":
    startScreen()
