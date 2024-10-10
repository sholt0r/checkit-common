import requests as re
from common import log

def send_http_request(API_HOST, API_PORT, TOKEN, S_FUNC, LOGGER_NAME=None):
    try:
        logger = log.setup_logger(LOGGER_NAME)
        headers = {"Content-Type":"application/json", "Authorization":f"Bearer {TOKEN}"}
        json = {"function":f"{S_FUNC}"}
        response = re.post(f"https://{API_HOST}:{API_PORT}/api/v1", headers=headers, json=json)
        if response.status_code not in (200, 204):
            logger.error(f"Status code {response.status_code}.")
            return False
        if S_FUNC == "QueryServerState":
            logger.info("Query command successful.")
            return response.json()['data']['serverGameState']
        if S_FUNC == "Shutdown":
            logger.info("Shutdown command successful.")
            return True
    except Exception as err:
        logger.error(f"{err}")
        return False