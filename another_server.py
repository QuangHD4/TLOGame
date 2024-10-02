import socket, pickle, copy, json
from _thread import *

server = "192.168.1.2"
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen(2)
print("Waiting for a connection, Server Started")


players = {}

def threaded_client(conn, player_id):
    conn.send(pickle.dumps(player_id))
    # allocate space for player (might not be necessary)
    players[player_id] = None

    reply = ""
    while True:
        try:
            # try increasing 2048
            player_data = pickle.loads(conn.recv(2048))
            players[player_id] = player_data

            if not player_data:
                print("Disconnected")
                break
            else:
                reply = copy.deepcopy(players)
                reply.pop(player_id, None)
                print(reply)

                print("Received: ", player_data)
                print("Sending : ", reply)

            conn.sendall(pickle.dumps(reply))
        except:
            break

    print("Lost connection")
    conn.close()

currentPlayerID = 0
while True:
    conn, addr = s.accept()
    print("Connected to:", addr)

    start_new_thread(threaded_client, (conn, currentPlayerID))
    currentPlayerID += 1