import socket
import pickle
from Pygame_Tools import KeyData
import time



class Network:
    def __init__(self, ip, port):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addr = (ip, port)
        self.start = self.connect()
        self.p = tuple(self.start.keys())[0]

    def connect(self):
        try:
            self.client.connect(self.addr)
            data = pickle.loads(self.client.recv(5 * 2048))
            return data
        except socket.error as e:
            print(e)

    def send(self, data):
        try:
            self.client.send(pickle.dumps(data, protocol=-1))
            data = self.client.recv(5 * 2048)
            return pickle.loads(data)
        except socket.error as e:
            print(e)


if __name__ == '__main__':
    # Test case
    ip = "10.0.0.144"
    port = 7135
    network = Network(ip, port)
    print(network.p)


    player_data = KeyData(network.p)
    for i in range(network.p + 1):
        player_data.ships_pos[i] = [[10000000.1, 10.3], [10000000.1, 10.3], 10000000.4]
        player_data.new_weapons = [['S', [10.1, 10.2], [10.3, 10.4]]]
    print('starting stream')
    for x in range(10000):
        #time.sleep(1)
        player_data = network.send(player_data)
        print(player_data.new_weapons)
        player_data.new_weapons = [['r', [10, 10], [10, 10]]]
    print('finished')
    print(player_data.ships_pos)
    print(pickle.dumps(player_data, protocol=-1).__sizeof__())