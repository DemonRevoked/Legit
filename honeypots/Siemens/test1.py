import socket

req = b'\x00\x01\x00\x00\x00\x06\x01\x01\x00\x00\x00\x08'  # FC=0x01, Addr=0, Count=8
sock = socket.socket()
sock.connect(('127.0.0.1', 502))
sock.send(req)
print("Response:", sock.recv(1024).hex())
