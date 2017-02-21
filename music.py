from __future__ import print_function
import sys
import socket

#Getting instructions from the user in command prompt
get_cmd = sys.argv

'''
Features available to the user :
1. Add song 2. Remove song 3. Display songs  4. Play  5. Skip  6. Stop

Format in which user sends requests :
format : python connect.py <feature> <song_name>

To display playlist, user sends :
format : python connect.py list

Format in which request has to be sent to the server :
format : add/remove:<song_name>
'''

song_name = ''
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("192.168.43.205", 8000))
print("Connected to server.")

def send_songname(song_name):
    print("Sending instruction to the server...")
    sock.sendall(song_name.encode('utf-8'))
    print("Instruction sent\n")

def display_songs():
    songs = sock.recv(1024).decode('utf-8')
    list_of_songs = songs.split(':')
    print("Songs currently in the playlist : \n")
    for i in list_of_songs:
        print(i)

if(len(get_cmd) == 2):
    send_songname(get_cmd[1])
    print("printing list")
    display_songs()

else:
    for i in range(2, len(get_cmd)):
        song_name = song_name + get_cmd[i] + ' '
    print("Song name : " + song_name)
    if(get_cmd[1] == 'add'):
        song_name = "add:" + song_name
    elif(get_cmd[1] == 'remove'):
        song_name = "remove:" + song_name
    send_songname(song_name[:-1])
    display_songs()

sock.close()

