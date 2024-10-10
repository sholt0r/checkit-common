import socket, struct

PROTOCOL_MAGIC=0xF6D5
MESSAGE_TYPE_POLL=0
PROTOCOL_VERSION=1

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
