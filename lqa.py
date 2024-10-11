import socket, struct, time, select, asyncio
from common import log

# Define constants
PROTOCOL_MAGIC = 0xF6D5
PROTOCOL_VERSION = 1
MESSAGE_TYPE_POLL = 0  # Poll Server State

# Function to poll server state
async def poll_server_state(S_API_HOST, S_API_PORT, POLL_INTERVAL=0.05, LOGGER_NAME=None):
    logger = log.setupLogger(LOGGER_NAME)
    try:
        # Define server and create socketo
        server = (S_API_HOST, S_API_PORT)
        c_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        c_sock.setblocking(False)
        last_result = None

        while True:
            # Generate message with unique cookie
            cookie = int(time.time() * 1000)
            request_message = struct.pack('<HBBQ', PROTOCOL_MAGIC, MESSAGE_TYPE_POLL, PROTOCOL_VERSION, cookie) + b'\x01'

            c_sock.sendto(request_message, server)

            ready_to_read, _, _ = await asyncio.get_event_loop().run_in_executor(
                None, select.select, [c_sock], [], [], POLL_INTERVAL
            )

            if ready_to_read:
                response, _ = c_sock.recvfrom(1024)
                response_len = len(response)
                if response_len < 22:
                    logger.error(f"Response too short: {response_len} bytes")
                    return False
                if last_result is not None and has_state_changed(last_result, response):
                    logger.info(f"State change detected. Querying HTTP API...")
                    try: 
                        status = hta.send_http_request(S_API_HOST, S_API_PORT, S_TOKEN, "QueryServerState")
                        logger.info(f"Updated server status.")
                        server_state.update_state(status)
                    return response

            await asyncio.sleep(POLL_INTERVAL)

    except asyncio.CancelledError:
        logger.error("Poll server state loop cancelled, shuttind down...")
    finally:
        c_sock.close()

# Unpack the response header
header_format = '<HBBQBIQB'
header_size = struct.calcsize(header_format)
        
protocol_magic, message_type, protocol_version, response_cookie, server_state, server_net_cl, server_flags, num_sub_states = struct.unpack_from(header_format, response_message, 0)
        
# Verify if the response matches our request
# Get the server state (Idle, Loading, Playing, etc.)
# Calculate sub-state size and remaining message length
sub_states_size = num_sub_states * 3  # Each sub state is 1 byte + 2 bytes
        
# Check if there's enough data for sub-states and the server name length field
if response_length < header_size + sub_states_size + 2:  # 2 bytes for server name length
    raise ValueError("Response does not contain enough data for sub-states or server name length")
        
# Extract server name
server_name_length_offset = header_size + sub_states_size
server_name_length = struct.unpack_from('<H', response_message, server_name_length_offset)[0]
        
# Check if there's enough data for the server name
if response_length < server_name_length_offset + 2 + server_name_length:
    raise ValueError(f"Response too short to contain server name. Expected at least {server_name_length_offset + 2 + server_name_length}, got {response_length}")
        
server_name_offset = server_name_length_offset + 2  # 2 bytes for length
server_name = response_message[server_name_offset:server_name_offset + server_name_length].decode('utf-8')
