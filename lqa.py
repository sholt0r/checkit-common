import socket, struct, time, select, asyncio


PROTOCOL_MAGIC = 0xF6D5
PROTOCOL_VERSION = 1
MESSAGE_TYPE_POLL = 0
MESSAGE_TYPE_RESPONSE = 1


class LWAResponse:
    def __init__(self, protocol_magic, message_type, protocol_version, response_cookie,
                 server_state, server_net_cl, server_flags, num_sub_states):
        self.protocol_magic = protocol_magic
        self.message_type = message_type
        self.protocol_version = protocol_version
        self.cookie = response_cookie
        self.server_state = server_state
        self.server_net_cl = server_net_cl
        self.server_flags = server_flags
        self.num_sub_states = num_sub_states


async def poll_server_state(host, port, poll_interval=0.05):
    server = (host, port)
    c_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    c_sock.setblocking(False)

    try:
        # Generate message with unique cookie
        cookie = int(time.time() * 1000)
        request_message = struct.pack('<HBBQ', PROTOCOL_MAGIC, MESSAGE_TYPE_POLL, PROTOCOL_VERSION, cookie) + b'\x01'

        c_sock.sendto(request_message, server)

        ready_to_read, _, _ = await asyncio.get_event_loop().run_in_executor(
            None, select.select, [c_sock], [], [], poll_interval
        )

        if ready_to_read:
            response, _ = c_sock.recvfrom(1024)
            response_len = len(sock_response)
            if response_len < 22:
                raise ValueError(f"Response too short: {response_len} bytes")
            
            header_format = '<HBBQBIQB'
            header_size = struct.calcsize(header_format)
            state = LWAResponse(*struct.unpack_from(header_format, sock_response, 0))
            sub_states_size = state.num_sub_states * 3
            server_name_length_offset = header_size + sub_states_size
            server_name_length = struct.unpack_from('<H', response, server_name_length_offset)[0]

            if state.protocol_magic != PROTOCOL_MAGIC or state.message_type != MESSAGE_TYPE_RESPONSE or state.cookie != cookie:
                raise ValueError('Unexpected state or mismatched cookie.')

            if response_len < header_size + sub_states_size + 2:  # 2 bytes for server name length
                raise ValueError("Response does not contain enough data for sub-states or server name length")

            if response_len < server_name_length_offset + 2 + server_name_length:
                raise ValueError(f"Response too short to contain server name. Expected at least {server_name_length_offset + 2 + server_name_length}, got {response_len}")

            return response

        await asyncio.sleep(poll_interval)

    except asyncio.CancelledError:
        return False, "err_can"
    finally:
        c_sock.close()

async def track_state(host, port):
    previous_state = None
    state = poll_server_state(host, port)

