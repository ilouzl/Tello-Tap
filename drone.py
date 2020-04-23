import curses
import socket
from time import sleep
import asyncio
from easytello import tello

my_drone = tello.Tello()

INTERVAL = 0.2


stats = {}

def report(str):
    stdscr.addstr(0, 0, str)
    stdscr.refresh()

if __name__ == "__main__":
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()

    local_ip = ''
    local_port = 8890
    socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # socket for sending cmd
    socket.bind((local_ip, local_port))

    tello_ip = '192.168.10.1'
    tello_port = 8889
    tello_adderss = (tello_ip, tello_port)

    socket.sendto('command'.encode('utf-8'), tello_adderss)

    try:
        index = 0
        while True:
            index += 1
            response, ip = socket.recvfrom(1024)
            if response == 'ok':
                continue
            response = response.decode('utf8')
            out = response.replace(';', ';\n')
            out = 'Tello State:\n' + out
            for s in response.split(';'):
                v = s.split(':')
                stats[v[0]] = int(v[1])

            report(str(stats))
            sleep(INTERVAL)
    except KeyboardInterrupt:
        curses.echo()
        curses.nocbreak()
        curses.endwin()
