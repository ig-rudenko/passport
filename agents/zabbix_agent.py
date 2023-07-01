import os
import logging
import sys

os.environ.setdefault("ZABBIX_URL", "http://192.168.31.201")
os.environ.setdefault("ZABBIX_LOGIN", "irudenko")
os.environ.setdefault("ZABBIX_PASSWORD", "opWu0Elh")
os.environ.setdefault("ZABBIX_VERIFY_SESSION", "1")
os.environ.setdefault("AGENT_TOKEN", "12345")
os.environ.setdefault("PASSPORT_DOMAIN", "http://127.0.0.1:8000")


from zabbix.generator import ZabbixGenerator
from base.agent import Agent
from base.connector import Connector

if __name__ == "__main__":
    token = os.getenv("AGENT_TOKEN")
    passport_domain = os.getenv("PASSPORT_DOMAIN")

    logger = logging.getLogger(__name__)
    logging.basicConfig(
        level=logging.INFO,
        # filename="py_log.log",
        filemode="a",
        stream=sys.stdout,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    logger.info(f"\n{'#'*20} RUN AGENT {'#'*20}")

    connector = Connector(token=token, domain=passport_domain)
    if connector.check_connection():
        logger.info(f"Connection to PassPort established successfully")
    else:
        logger.info(f"Connection to PassPort refused")
        sys.exit(1)

    agent = Agent(
        connector=connector,
        generator=ZabbixGenerator(),
    )

    try:
        agent.start()
    except KeyboardInterrupt:
        # Отправляем секреты, которые могли быть созданы в момент прерывания
        agent.send_new_secrets()

    logger.info(f"\n{'#'*20} AGENT STOPPED {'#'*20}")
