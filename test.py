#!/Users/jstaples/Development/checkit/.venv/bin/python3.12
import socket, struct, time, select, statistics

SERVER=("ficsit.thebois.au", 7777)
PROTOCOL_MAGIC=0xF6D5
MESSAGE_TYPE_POLL=0
PROTOCOL_VERSION=1

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(False)

    num_pings = 10
    timeout = 1
    rtt_list = []

    cookie = int(time.time() * 1000)
    request_message = struct.pack('<HBBQ', PROTOCOL_MAGIC, MESSAGE_TYPE_POLL, PROTOCOL_VERSION, cookie) + b'\x01'

    print(f"Measuring response delay over {num_pings} pings...")

    for i in range(num_pings):
        start_time = time.time()
        sock.sendto(request_message, SERVER)

        ready_to_read, _, _ = select.select([sock], [], [], timeout)

        if ready_to_read:
            data, server = sock.recvfrom(1024)

            end_time = time.time()

            rtt = end_time - start_time
            rtt_list.append(rtt)

            print(f"Response {i+1}: {data} - RTT: {rtt:.6f} seconds")
        else:
            print(f"Ping {i+1}: Request timed out")

except socket.error as e:
    print(f"Error: {e}")

finally:
    sock.close()

if rtt_list:
    avg_rtt = statistics.mean(rtt_list)
    max_rtt = max(rtt_list)
    min_rtt = min(rtt_list)

    print(f"\nAverage RTT: {avg_rtt:.6f} seconds")
    print(f"Maximum RTT: {max_rtt:.6f} seconds")
    print(f"Minimum RTT: {min_rtt:.6f} seconds")
else:
    print(f"\nNo responses received")

