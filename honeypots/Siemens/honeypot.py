import socket
import json
import threading
import time
from datetime import datetime

# Load PLC config
with open("registers.json") as f:
    config = json.load(f)

device_info = config.get("device_info", {})
holding_registers = config.get("holding_registers", {})
coils = config.get("coils", {})
dynamic = config.get("dynamic", {}).get("holding_registers", {})
locked_registers = ["10", "99"]

LOGFILE = "honeypot_log.txt"
LOCK = threading.Lock()
session_tracker = {}

# Background updater
def dynamic_update_loop():
    while True:
        time.sleep(5)
        with LOCK:
            for reg, rule in dynamic.items():
                reg = str(reg)
                current = holding_registers.get(reg, rule["start_value"])
                new_val = current + rule["step"]
                if new_val > rule["max"]:
                    new_val = rule["start_value"]
                holding_registers[reg] = new_val

# Logging
def log_event(addr, fc, start, note):
    with open(LOGFILE, "a") as f:
        f.write(f"{datetime.now()} - {addr[0]}:{addr[1]} - FC:{fc} - Start:{start} - {note}\n")

def update_session(ip, action):
    if ip not in session_tracker:
        session_tracker[ip] = []
    session_tracker[ip].append((datetime.now(), action))

# Response builders
def build_response(tid, uid, payload):
    length = len(payload) + 1  # 1 byte for UID
    header = tid + b'\x00\x00' + length.to_bytes(2, 'big') + bytes([uid])
    return header + payload

def build_exception(tid, uid, fc, code):
    return build_response(tid, uid, bytes([fc | 0x80, code]))

# Function Codes
def handle_read_holding(tid, uid, start, qty):
    with LOCK:
        values = [holding_registers.get(str(i), 0) for i in range(start, start + qty)]
    payload = b'\x03' + bytes([qty * 2]) + b''.join(val.to_bytes(2, 'big') for val in values)
    return build_response(tid, uid, payload)

def handle_read_input_registers(tid, uid, start, qty):
    with LOCK:
        values = [holding_registers.get(str(i), 0) for i in range(start, start + qty)]
    payload = b'\x04' + bytes([qty * 2]) + b''.join(val.to_bytes(2, 'big') for val in values)
    return build_response(tid, uid, payload)

def handle_read_coils(tid, uid, start, qty):
    with LOCK:
        bits = ''.join(str(coils.get(str(i), 0)) for i in range(start, start + qty))

    # Pad bits if too short
    bits = bits.ljust(qty, '0')

    bit_bytes = int(bits[::-1], 2).to_bytes((len(bits) + 7) // 8, 'little')
    payload = b'\x01' + bytes([len(bit_bytes)]) + bit_bytes
    return build_response(tid, uid, payload)


def handle_write_single(tid, uid, start, value, addr):
    if str(start) in locked_registers:
        log_event(addr, 6, start, f"⚠️ Write to LOCKED register: {value}")
        return build_exception(tid, uid, 0x06, 0x02)
    with LOCK:
        holding_registers[str(start)] = value
    update_session(addr[0], f"FC:06 to {start} = {value}")
    log_event(addr, 6, start, f"SingleWrite: {value}")
    payload = b'\x06' + start.to_bytes(2, 'big') + value.to_bytes(2, 'big')
    return build_response(tid, uid, payload)

def handle_write_multiple(tid, uid, start, qty, data_block, addr):
    if any(str(start + i) in locked_registers for i in range(qty)):
        blocked_vals = [int.from_bytes(data_block[i*2:(i+1)*2], 'big') for i in range(qty)]
        log_event(addr, 16, start, f"⚠️ Multi-write to LOCKED registers: {blocked_vals}")
        return build_exception(tid, uid, 0x10, 0x02)
    with LOCK:
        for i in range(qty):
            val = int.from_bytes(data_block[i*2:(i+1)*2], 'big')
            holding_registers[str(start + i)] = val
    update_session(addr[0], f"FC:10 write {qty} registers starting {start}")
    log_event(addr, 16, start, f"MultiWrite: {qty} regs")
    payload = b'\x10' + start.to_bytes(2, 'big') + qty.to_bytes(2, 'big')
    return build_response(tid, uid, payload)

def handle_device_id_request(tid, uid):
    id_fields = [
        (0x00, device_info.get("vendor", "Unknown")),
        (0x01, device_info.get("model", "Unknown")),
        (0x02, device_info.get("firmware", "0.0.0"))
    ]
    data = b'\x2b\x0e\x01\x00\x00' + bytes([len(id_fields)])
    for obj_id, val in id_fields:
        enc = val.encode()
        data += bytes([obj_id, len(enc)]) + enc
    return build_response(tid, uid, data)

def handle_report_slave_id(tid, uid):
    slave_id = 1
    status = 0xFF
    id_str = f"{device_info.get('vendor')} {device_info.get('model')}".encode()
    payload = b'\x11' + bytes([2 + len(id_str)]) + bytes([slave_id, status]) + id_str
    return build_response(tid, uid, payload)

# Main Server
def start_server():
    HOST, PORT = "0.0.0.0", 502
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    sock.listen(5)
    print(f"[*] Modbus Honeypot running on port {PORT} - {device_info.get('vendor')} {device_info.get('model')}")

    while True:
        conn, addr = sock.accept()
        try:
            data = conn.recv(1024)
            if len(data) < 8:
                conn.close(); continue

            tid, uid, fc = data[0:2], data[6], data[7]
            print(f"[DEBUG] FC={fc:02X} from {addr[0]}:{addr[1]}")

            if fc == 0x03:
                start = int.from_bytes(data[8:10], 'big')
                qty = int.from_bytes(data[10:12], 'big')
                conn.sendall(handle_read_holding(tid, uid, start, qty))

            elif fc == 0x04:
                start = int.from_bytes(data[8:10], 'big')
                qty = int.from_bytes(data[10:12], 'big')
                conn.sendall(handle_read_input_registers(tid, uid, start, qty))

            elif fc == 0x01:
                start = int.from_bytes(data[8:10], 'big')
                qty = int.from_bytes(data[10:12], 'big')
                print(f"[DEBUG] Handling Read Coils: start={start}, qty={qty}")
                response = handle_read_coils(tid, uid, start, qty)
                print(f"[DEBUG] Coil Response: {response.hex()}")
                conn.sendall(response)

            elif fc == 0x06:
                start = int.from_bytes(data[8:10], 'big')
                val = int.from_bytes(data[10:12], 'big')
                conn.sendall(handle_write_single(tid, uid, start, val, addr))

            elif fc == 0x10:
                start = int.from_bytes(data[8:10], 'big')
                qty = int.from_bytes(data[10:12], 'big')
                byte_count = data[12]
                data_block = data[13:13+byte_count]
                conn.sendall(handle_write_multiple(tid, uid, start, qty, data_block, addr))

            elif fc == 0x2b and data[8] == 0x0e:
                log_event(addr, fc, 0, "Read Device Identification")
                conn.sendall(handle_device_id_request(tid, uid))

            elif fc == 0x11:
                log_event(addr, fc, 0, "Report Slave ID")
                conn.sendall(handle_report_slave_id(tid, uid))

            else:
                print(f"[!] Unsupported FC: {fc}")

        except Exception as e:
            print(f"[!] Error from {addr[0]}: {e}")
        finally:
            conn.close()

if __name__ == "__main__":
    threading.Thread(target=dynamic_update_loop, daemon=True).start()
    start_server()
