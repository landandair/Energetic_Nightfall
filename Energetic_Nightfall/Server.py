import socket
import _thread as thread
import pickle
import time

import numpy as np
from Pygame_Tools import KeyData

Debug = True

def main():
    """To start a server, Follow these steps
    - Go to your network settings and find the local Ip Address
    - Copy the address into the server field shown below
    - Change the port number if desired and run the script"""
    # Put server and com port here
    server = "10.0.0.144"
    port = 7135
    debug = True
    # set the communication protocol
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:  # bind the socket object to the ip and port
        s.bind((server, port))
    except socket.error as e:
        print(e)

    s.listen(2)
    print("Waiting for a connection, Server Started")
    # Used to assign ship ids to clients
    connections = {}
    current_player = 0
    while True:  # Main connection loop which listens and creates threads that handle communications with clients
        conn, addr = s.accept()
        print("Connected to:", addr)
        # Check if this ip has been connected to in the past and feeds it back its ship id
        if addr[0] in connections.keys() and not debug:
            player = connections[addr[0]]
        else:
            player = current_player
            connections[addr[0]] = player
            current_player += 1
        # Start thread to manage player
        thread.start_new_thread(threaded_client, (conn, player))


class ServerData:
    def __init__(self):
        """Class which holds all of the data that the server needs to keep track of in order to pass data from
        one client to the other
        contents:
            -ship_pos: {} with key (id) and values
                [pos <vector>, vel <vector>, heading <float>, health <int>, status <str>]
            -new_weapons: [] with contents of [type <str>, pos <vector>, vel <vector>, target <vetor> or id <int>]
            -wep_mail: {} with key (id) and values of [] with contents of [] in format
                [type <str>, pos <vector>, vel <vector>, target <vetor> or id <int>]
            -id: int player # of the ship most recently connected by a player"""
        self.ships_pos = {}
        self.new_weapons = []
        self.wep_mail = {}
        self.id = 0

    def add_wep_mail(self, id, weapons):
        """Takes the new weapon list given by one of the players by id number and adds those weapons into lists of
        weapons to be sent out to the other players to add the presence of that weapon on their screen
        inputs:
            - id <int>: player key who fired the weapons
            - weapons [list]: contains lists of format
            [type <str>, pos <vector>, vel <vector>, target <vetor> or id <int>]"""
        for ship in self.ships_pos.keys():
            if ship not in self.wep_mail.keys():
                self.wep_mail[ship] = []
            if ship != id:
                self.wep_mail[ship].extend(weapons)


Server_data = ServerData()


def threaded_client(conn, player):
    Server_data.id = player
    if player in Server_data.ships_pos.keys():
        initial = {player: Server_data.ships_pos[player]}
    else:
        initial = {player: [np.array((200, 100)), np.array((0, 0)), 0, 100, False]}
    conn.send(pickle.dumps(initial, protocol=-1))
    Server_data.wep_mail[player] = []
    while True:
        try:
            data = conn.recv(5 * 2048)
            if not data:
                print(f"Player {player} Disconnected")
                Server_data.ships_pos[player][3] = 0  # Kills disconnected ship for all clients by setting health to 0
                break
            data = pickle.loads(data)

            Server_data.ships_pos[player] = data.ships_pos[player]
            data.ships_pos = Server_data.ships_pos
            if data.new_weapons:
                new_weapons = data.new_weapons
                Server_data.add_wep_mail(player, new_weapons)

            data.new_weapons = Server_data.wep_mail[player]
            Server_data.wep_mail[player] = []

            # print('sending', pickle.dumps(data).__sizeof__(), 'bytes')
            conn.sendall(pickle.dumps(data, protocol=-1))
            # print("Sent : ", data, player)
        except socket.error as e:
            print(e)
            break
    time.sleep(5)
    Server_data.wep_mail.pop(player)
    Server_data.ships_pos.pop(player)  # Removes disconnected player from memory
    print(f"Lost connection to player:{player}")
    conn.close()


if __name__ == '__main__':
    main()
