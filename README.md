# UDP Server State Query Script

This Python script interacts with a Satisfactory server using its lightweight UDP-based query protocol to retrieve the current state, including its name, status (Idle, Loading, Playing), and additional metadata.

## Features

- Polls the server to retrieve its state using UDP.
- Handles different server states such as Idle, Loading, and Playing.
- Extracts and returns server name, network changelist, flags, and sub-states.

## Requirements

- Python 3.12+
- A server supporting the described UDP protocol.

## Usage

1. Clone the repository or download the script.
2. Run the script with the server's address as input.

```python
server_info = poll_server_state('server_address_here')

if server_info:
    print(f"Server Name: {server_info['server_name']}")
    print(f"Server State: {server_info['state']}")
    print(f"Game Changelist: {server_info['server_net_cl']}")
    print(f"Number of Sub States: {server_info['num_sub_states']}")
```

3. The script will print the server's state and details or handle timeouts and errors gracefully.

## How it Works

- **Poll Request**: The script sends a UDP request (`Poll Server State`) containing a unique cookie to the server.
- **Response**: The server responds with its current state (`Server State Response`), and the script parses it for details like the server's state, name, flags, and changelist.
- **Error Handling**: The script handles response timeouts and invalid responses gracefully.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
