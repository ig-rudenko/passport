import logging
import os
import sys

os.environ.setdefault("ZABBIX_URL", "http://192.168.31.201")
os.environ.setdefault("ZABBIX_LOGIN", "irudenko")
os.environ.setdefault("ZABBIX_PASSWORD", "opWu0Elh")
os.environ.setdefault("ZABBIX_VERIFY_SESSION", "1")
os.environ.setdefault("AGENT_TOKEN", "12345")
os.environ.setdefault("PASSPORT_BASE_API_URL", "http://127.0.0.1:8000/api/v1/")

from zabbix.generator import ZabbixGenerator
from base.agent import Agent
from base.connector import Connector

logger = logging.getLogger(__name__)


def get_passport_base_api_url() -> str:
    passport_base_url = os.getenv("PASSPORT_BASE_API_URL")
    if passport_base_url.endswith("/"):
        passport_base_url = passport_base_url[:-1]
    return passport_base_url


if __name__ == "__main__":
    token = os.getenv("AGENT_TOKEN")
    logging.basicConfig(
        level=logging.INFO,
        # filename="py_log.log",
        filemode="a",
        stream=sys.stdout,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    logger.info(f"\n{'#' * 20} RUN AGENT {'#' * 20}")

    connector = Connector(token=token, base_url=get_passport_base_api_url())
    if connector.check_connection():
        logger.info(f"Connection to PassPort established successfully")
    else:
        logger.info(f"Connection to PassPort refused")
        sys.exit(1)

    agent = Agent(
        connector=connector,
        generator=ZabbixGenerator(),
        period=2,
    )

    try:
        agent.start()
    except KeyboardInterrupt:
        # Отправляем секреты, которые могли быть созданы в момент прерывания
        agent.send_new_secrets()

    logger.info(f"\n{'#' * 20} AGENT STOPPED {'#' * 20}")
