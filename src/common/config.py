import logging
import os

from dotenv import load_dotenv
from pika import ConnectionParameters, BlockingConnection

load_dotenv('.env')

from django.conf import settings as django_settings

logger = logging.getLogger(__name__)

ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
SPECIAL_VK_ACC_SERVICE_KEY = os.getenv('SPECIAL_VK_ACC_SERVICE_KEY')

_connection = None
_channel = None


def get_connection_params():
    return ConnectionParameters(
        host=django_settings.RABBITMQ_HOST,
        port=django_settings.RABBITMQ_PORT,
        heartbeat=django_settings.RABBITMQ_HEARTBEAT,
        connection_attempts=django_settings.RABBITMQ_CONNECTION_ATTEMPTS,
        retry_delay=django_settings.RABBITMQ_RETRY_DELAY,
        blocked_connection_timeout=300,
    )


def _is_connection_open():
    try:
        if _connection is None:
            return False
        return _connection.is_open and not _connection.is_closed
    except Exception:
        return False


def reset_connection():
    global _connection, _channel
    if _connection is not None:
        try:
            _connection.close()
        except Exception:
            pass
    _connection = None
    _channel = None


def get_channel(queue="abs-stats"):
    global _connection, _channel

    if not _is_connection_open():
        logger.info("Подключение к RabbitMQ по адресу %s:%s", django_settings.RABBITMQ_HOST,
                    django_settings.RABBITMQ_PORT)
        params = get_connection_params()
        _connection = BlockingConnection(params)
        _channel = _connection.channel()
        _channel.queue_declare(queue=queue, durable=True)
        logger.info("Подключение к RabbitMQ установлено")
    elif _channel is None or _channel.is_closed:
        _channel = _connection.channel()
        _channel.queue_declare(queue=queue, durable=True)

    return _channel
