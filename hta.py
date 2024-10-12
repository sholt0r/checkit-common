from email.mime import application
import requests as re
import log

class HTTPServerState:
    def __init__(self, host, port, token, logger_name=None):
        self.host = host
        self.port = port
        self.token = token
        self.logger_name = logger_name

        self.url = f'https://{self.host}:{self.port}/api/v1'
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}' 
        }

        self.active_session = None
        self.num_players = None
        self.player_limit = None
        self.tech_tier = None
    
    def get_nested(self, dictionary, keys, default=None):
        for key in keys:
            dictionary = dictionary.get(key, default)
            if dictionary is default:
                break
        return dictionary

    def get_server_state(self):
        json = {'function': 'QueryServerState'}
        response = re.post(self.url, self.headers, json)
        self.update_local_state(self.get_nested(response, ['data', 'serverGameState'], 'Unknown Response'))

    def restart_server(self):
        json = {'function': 'Shutdown'}
        re.post(self.url, self.headers, json)
        self.update_local_state(restart=True)

    def update_local_state(self, status=None, restart=False):
        if restart:
            self.active_session = None
            self.num_players = None
            self.player_limit = None
            self.tech_tier = None
            return
        
        self.active_session = status.get('activeSessionName')
        self.num_players = status.get('numConnectedPlayers')
        self.player_limit = status.get('playerLimit')
        self.tech_tier = status.get('techTier')

    def __repr__(self):
        return (f"Active Session: {self.active_session}\n"
                f"Number of Players: {self.active_session}/{self.player_limit}\n"
                f"Tech Tier: {self.tech_tier}")

def send_http_request(API_HOST, API_PORT, TOKEN, S_FUNC, LOGGER_NAME=None):
    try:
        logger = log.setup_logger(LOGGER_NAME)
        logger.info("Logging initialized for hta")
        
        headers = {"Content-Type":"application/json", "Authorization":f"Bearer {TOKEN}"}
        json = {"function":f"{S_FUNC}"}
        response = re.post(f"https://{API_HOST}:{API_PORT}/api/v1", headers=headers, json=json)
        if response.status_code not in (200, 204):
            logger.info(f"Status code {response.status_code}")
            return False
        if S_FUNC == "QueryServerState":
            logger.info("Query command successful")
            return response.json()['data']['serverGameState']
        if S_FUNC == "Shutdown":
            logger.info("Shutdown command successful")
            return True
    except Exception as err:
        logger.info(f"{err}")
        return False
