import requests as re


class HTTPServerState:
    def __init__(self, host, port, token):
        self.host = host
        self.port = port
        self.token = token

        self.url = f'https://{self.host}:{self.port}/api/v1'
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}' 
        }

        self.update_local_state()


    def get_nested(self, dictionary, keys, default=None):
        for key in keys:
            dictionary = dictionary.get(key, default)
            if dictionary is default:
                break
        return dictionary


    def query_server_state(self):
        json = {'function': 'QueryServerState'}
        response = re.post(self.url, self.headers, json)
        state = self.get_nested(response.json(), ['data', 'serverGameState'], 'Unknown Response')
        return state


    def restart_server(self):
        json = {'function': 'Shutdown'}
        re.post(self.url, self.headers, json)
        return True


    def update_local_state(self):
        self.local_state = self.query_server_state()
        self.active_session = self.local_state.get('activeSessionName')
        self.num_players = self.local_state.get('numConnectedPlayers')
        self.player_limit = self.local_state.get('playerLimit')
        self.tech_tier = self.local_state.get('techTier')


    def __repr__(self):
        return (f"Active Session: {self.active_session}\n"
                f"Number of Players: {self.active_session}/{self.player_limit}\n"
                f"Tech Tier: {self.tech_tier}")

