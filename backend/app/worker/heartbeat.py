

import logging

logger = logging.getLogger()

def heartbeat_worker():
    logger.info("\033[94mHeartbeat worker running\033[0m")
    return