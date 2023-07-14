import os
import logging
import sys

from agents.zabbix.generator import ZabbixGenerator
from agents.base.agent import Agent
from agents.base.connector import Connector


def check_connection(conn: Connector) -> None:
    if conn.check_connection():
        logger.info(f"Connection to PassPort established successfully")
    else:
        logger.info(f"Connection to PassPort refused")
        sys.exit(1)


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
    check_connection(connector)

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
