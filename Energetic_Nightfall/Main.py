import pygame as pg
import Game_Sim as Game
import numpy as np
from Networking import KeyData, Network
SIZE = (1280, 720)

def main():
    ip = "10.0.0.144"
    port = 7135
    pg.init()
    pg.font.init()
    screen = pg.display.set_mode(SIZE)
    pg.display.set_caption('Energetic Nightfall')

    # Connect to server and create controlled ship with id
    print(f'connecting to {ip}')
    network = Network(ip, port)
    id = network.p
    print('connected')
    player_data = KeyData(id)
    print('Player Number: ' + str(id))
    player_data.ships_pos[id] = network.start[id]
    player_data = network.send(player_data)
    ship = Game.Ship(id, player_data.ships_pos[id], is_controllable=True)
    # except:
    #     network = False
    #     ship = Game.Ship(0, np.array((100, 100)), False, is_controllable=True)
    # Make initial ship
    ships = [ship]
    print(player_data.ships_pos)
    for ship in player_data.ships_pos.keys():
        if ship != id and player_data.ships_pos[ship][3] > 0:
            ship = Game.Ship(ship, player_data.ships_pos[ship], is_controllable=False)
            ships.append(ship)
    game_loop = Game.Game(screen, network, player_data, ships)
    while True:
        game_loop.update()


if __name__ == '__main__':
    """To Run this game:
    -first ensure a Server is running(can run on the same machine as the game)
    -Change the ip variable to be the local ip of the server you wish to connect to
    -Change the port # to match the port the server is on
    -Run the script
    """
    main()
