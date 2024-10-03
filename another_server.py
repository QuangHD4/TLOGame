import socket, pickle, copy, json
from _thread import *

server = "192.168.1.2"
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen()
print("Waiting for a connection, Server Started")


players = {}
max_player_num = 30
available_spots = [None]*max_player_num
for i in range(max_player_num):
    available_spots[i] = (max_player_num - 1) - i
print(available_spots)

def threaded_client(conn, player_id):
    conn.send(pickle.dumps(player_id))
    # allocate space for player (might not be necessary)
    # players[player_id] = None

    reply = ""
    while True:
        try:
            player_data = pickle.loads(conn.recv(2048))
            players[player_id] = player_data

            if not player_data:
                print("Disconnected")
                break
            else:
                reply = copy.deepcopy(players)
                reply.pop(player_id, None)

            conn.sendall(pickle.dumps(reply, protocol=pickle.HIGHEST_PROTOCOL))
        except:
            break

    print("Lost connection")
    conn.close()
    players.pop(player_id)
    available_spots.append(player_id)

while True:
    conn, addr = s.accept()
    print("Connected to:", addr)

    currentPlayerID = available_spots.pop()
    start_new_thread(threaded_client, (conn, currentPlayerID))