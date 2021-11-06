import socket

from utils.server import *

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', 9080))
print('Server started')

while True:
    data, addres = sock.recvfrom(1024)
    data = data.decode("utf-8")

    parse_request(sock, addres, data)
