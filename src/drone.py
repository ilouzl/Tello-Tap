import curses
import socket
from time import sleep
import asyncio
from easytello.tello import Tello


class MyTello(Tello):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.stats = {}
        self.local_port_stats = 8890
        self.stats_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # socket for sending cmd
        self.stats_socket.bind((self.local_ip, self.local_port_stats))
        self.stats_socket.sendto('command'.encode('utf-8'), self.tello_address)
    
    def read_stats(self):
        response, ip = self.stats_socket.recvfrom(1024)
        if response == 'ok':
            return
        response = response.decode('utf8')
        out = response.replace(';', ';\n').rstrip('\r\n')
        if self.debug is True:
            print('Tello State:\n' + out)
        response = response.rstrip(';\r\n')
        for s in response.split(';'):
            v = s.split(':')
            self.stats[v[0]] = float(v[1])
            

if __name__ == "__main__":
    my_drone = MyTello()#tello_ip="127.0.0.1")
    while True:
        my_drone.read_stats()
        sleep(0.2)
