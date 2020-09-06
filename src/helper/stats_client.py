import socket
from time import sleep

 


serverAddressPort   = ("127.0.0.1", 8890)

bufferSize          = 1024

 

# Create a UDP socket at client side

UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

 

# Send to server using created UDP socket
cnt = 0
while True:
    # msgFromClient       = "Hello UDP Server %d \n" %(cnt)
    msgFromClient       = "msg:%d;pitch:0;roll:0;yaw:0;vgx:0;vgy:0;vgz:0;templ:74;temph:75;tof:6553;h:0;bat:100;baro:380.59;time:0;agx:5.00;agy:0.00;agz:-1002.00;\r\n" %(cnt)
    bytesToSend         = str.encode(msgFromClient)
    UDPClientSocket.sendto(bytesToSend, serverAddressPort)
    sleep(1)
    cnt += 1

 

msgFromServer = UDPClientSocket.recvfrom(bufferSize)

 

msg = "Message from Server {}".format(msgFromServer[0])

print(msg)