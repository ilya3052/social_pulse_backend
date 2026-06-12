import logging

import pika

from common.config import get_channel, reset_connection

logger = logging.getLogger(__name__)


def publish_task(message, queue='abs-stats'):
    for attempt in range(2):
        try:
            channel = get_channel()
            channel.basic_publish(
                exchange='',
                routing_key=queue,
                body=message
            )
            logger.info("Message published: %s", message)
            return
        except pika.exceptions.StreamLostError:
            logger.warning("Connection to RabbitMQ lost, reconnecting (attempt %d/2)", attempt + 1)
            print(f"Connection to RabbitMQ lost, reconnecting (attempt {attempt + 1}/2)")
            reset_connection()
    logger.error("Failed to publish message after reconnection")
