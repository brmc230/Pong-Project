Contact Info
============

Group Members & Email Addresses:

    Brooke McWilliams, brmc230@uky.edu
    Morgan Miller, mdmi240@uky.edu

Versioning
==========

V1 - Redundant server side that is no longer applicable
V2 - Partially complete server/client code
V3 - Fully functional client and server code

pongServerTest - Small test with changed code that is no longer used
Github EC/Fixup Branch - Attempt to allow multiple connections to the server (DOES NOT RUN)

Github Link: https://github.com/brmc230/Pong-Project

General Info
============

This program was written in python 3.11. Both contributors used VSCode to write and test the program
where it was connected to a Github repo to track the way the game was being implemented with different 
versions and changing

Install Instructions
====================

Run the following line to install the required libraries for this project:

`pip3 install -r requirements.txt`

Known Bugs
==========
When the clients are presented with the end of game message, if one client decides to disconnect the other is not aware if they press "R" to restart the game and nothing will happen
If connections to the clients go wrong, the server side implementation does not 'smoothy' close down, errors are printed to the terminal and it is forcefully closed down

