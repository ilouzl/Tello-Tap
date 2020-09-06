import socket
from time import sleep

 


serverAddressPort   = ("127.0.0.1", 8890)

bufferSize          = 1024

 

# Create a UDP socket at client side

UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

 

# Send to server using created UDP socket
cnt = 0
while True:
    msgFromClient       = "Hello UDP Server %d \n" %(cnt)
    bytesToSend         = str.encode(msgFromClient)
    UDPClientSocket.sendto(bytesToSend, serverAddressPort)
    sleep(0.1)
    cnt += 1

 

msgFromServer = UDPClientSocket.recvfrom(bufferSize)

 

msg = "Message from Server {}".format(msgFromServer[0])

print(msg)