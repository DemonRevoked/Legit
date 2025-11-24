import socket

def build_modbus_request(tid, uid, function_code, start_addr, count):
    mbap = tid.to_bytes(2, 'big') + b'\x00\x00\x00\x06' + bytes([uid])
    pdu = bytes([function_code]) + start_addr.to_bytes(2, 'big') + count.to_bytes(2, 'big')
    return mbap + pdu

HOST = '10.0.44.102'
PORT = 502
request = build_modbus_request(tid=1, uid=1, function_code=0x01, start_addr=0, count=8)

sock = socket.socket()
sock.connect((HOST, PORT))
sock.sendall(request)
response = sock.recv(1024)
print("Response:", response.hex())
sock.close()
