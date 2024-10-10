import socket
import struct
import time
from common import log

# Define constants
PROTOCOL_MAGIC = 0xF6D5
PROTOCOL_VERSION = 1
MESSAGE_TYPE_POLL = 0  # Poll Server State
MESSAGE_TYPE_RESPONSE = 1  # Server State Response
SERVER_STATE_ENUM = ['Offline', 'Idle', 'Loading', 'Playing']

# Function to poll server state
def poll_server_state(S_API_HOST, S_API_PORT, TIMEOUT=5, LOGGER_NAME=None):
    try:
        logger = log.setupLogger(LOGGER_NAME)
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setTIMEOUT(TIMEOUT)
        
        # Generate a unique cookie (use current time as cookie)
        cookie = int(time.time() * 1000)
        
        # Prepare the "Poll Server State" request message
        request_message = struct.pack('<HBBQ', PROTOCOL_MAGIC, MESSAGE_TYPE_POLL, PROTOCOL_VERSION, cookie) + b'\x01'
    
    
        # Send the request to the server
        sock.sendto(request_message, (S_API_HOST, S_API_PORT))
        
        # Receive the response
        response_message, _ = sock.recvfrom(1024)  # Buffer size is 1024 bytes
        response_length = len(response_message)
        
        # Minimum size check
        if response_length < 22:  # Header size without sub-states and server name
            raise ValueError(f"Response too short: {response_length} bytes")
        
        # Unpack the response header
        header_format = '<HBBQBIQB'
        header_size = struct.calcsize(header_format)
        
        protocol_magic, message_type, protocol_version, response_cookie, server_state, server_net_cl, server_flags, num_sub_states = struct.unpack_from(header_format, response_message, 0)
        
        # Verify if the response matches our request
        if protocol_magic != PROTOCOL_MAGIC or message_type != MESSAGE_TYPE_RESPONSE or response_cookie != cookie:
            raise ValueError('Unexpected response or mismatched cookie.')
        
        # Get the server state (Idle, Loading, Playing, etc.)
        state_name = SERVER_STATE_ENUM[server_state] if server_state < len(SERVER_STATE_ENUM) else 'Unknown'
        
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
        
        # Return parsed server info
        return {
            'state': state_name,
            'server_name': server_name,
            'server_net_cl': server_net_cl,
            'server_flags': server_flags,
            'num_sub_states': num_sub_states
        }
    
    except socket.TIMEOUT:
        logger.info("Request timed out")
        return None
    except ValueError as ve:
        logger.info(f"{ve}")
        return None
    finally:
        sock.close()
