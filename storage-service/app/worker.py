import json
import logging
import signal
import sys
import time
import pika
from typing import Any, Dict

from .config import get_settings

logging.basicConfig(level=logging.INFO, format='[worker] %(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)
settings = get_settings()

_stop = False

def _signal_handler(sig, frame):
    global _stop
    logger.info(f"Received signal {sig}, shutting down...")
    _stop = True

signal.signal(signal.SIGINT, _signal_handler)
signal.signal(signal.SIGTERM, _signal_handler)


def process_message(msg: Dict[str, Any]):
    """Process a single message from the uploads queue. Safe and idempotent.
    Currently logs the event; extend to update stats, trigger scans, etc.
    """
    evt_type = msg.get("type")
    file_id = msg.get("file_id")
    user_id = msg.get("user_id")
    logger.info(f"Handled event {evt_type} for file {file_id} by user {user_id}")


def main():
    url = settings.rabbitmq_url
    logger.info(f"Connecting to RabbitMQ at {url}...")

    params = pika.URLParameters(url)
    while not _stop:
        try:
            conn = pika.BlockingConnection(params)
            channel = conn.channel()
            channel.queue_declare(queue="uploads", durable=True, arguments={
                "x-dead-letter-exchange": "",
                "x-dead-letter-routing-key": "uploads.dlq",
            })
            channel.queue_declare(queue="uploads.dlq", durable=True)

            def callback(ch, method, properties, body):
                try:
                    msg = json.loads(body.decode("utf-8"))
                except Exception:
                    msg = {"raw": str(body)[:200]}
                try:
                    process_message(msg)
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                except Exception as e:
                    logger.exception(f"Error processing message: {e}")
                    # Nack to DLQ
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

            channel.basic_qos(prefetch_count=10)
            channel.basic_consume(queue="uploads", on_message_callback=callback)
            logger.info("Worker started. Waiting for messages...")
            while not _stop:
                conn.process_data_events(time_limit=1)
            try:
                conn.close()
            except Exception:
                pass
        except Exception as e:
            logger.warning(f"RabbitMQ connection error: {e}; retrying in 3s...")
            time.sleep(3)


if __name__ == "__main__":
    main()
