import logging

from common.config import get_channel

logger = logging.getLogger(__name__)


def publish_task(message):
    try:
        channel = get_channel()
        channel.basic_publish(
            exchange='',
            routing_key='abs-stats',
            body=message
        )
        logger.info("Message published: %s", message)
    except Exception as e:
        logger.error("Failed to publish message: %s", e, exc_info=True)
