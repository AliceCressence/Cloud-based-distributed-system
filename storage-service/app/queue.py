import json
import logging
import pika
from typing import Any, Dict, Optional
from .config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def _connect():
    try:
        params = pika.URLParameters(settings.rabbitmq_url)
        return pika.BlockingConnection(params)
    except Exception as e:
        logger.warning(f"RabbitMQ connection failed: {e}")
        return None


def publish_json(queue_name: str, payload: Dict[str, Any], routing_key: Optional[str] = None) -> bool:
    """Publish a JSON message to a durable queue. Returns True on success, False otherwise."""
    conn = _connect()
    if not conn:
        return False
    try:
        ch = conn.channel()
        ch.queue_declare(queue=queue_name, durable=True, arguments={
            "x-dead-letter-exchange": "",
            "x-dead-letter-routing-key": f"{queue_name}.dlq",
        })
        # Ensure DLQ exists
        ch.queue_declare(queue=f"{queue_name}.dlq", durable=True)

        body = json.dumps(payload).encode("utf-8")
        ch.basic_publish(
            exchange="",
            routing_key=routing_key or queue_name,
            body=body,
            properties=pika.BasicProperties(
                delivery_mode=2,  # persistent
                content_type="application/json",
            ),
        )
        return True
    except Exception as e:
        logger.warning(f"Failed to publish message to {queue_name}: {e}")
        return False
    finally:
        try:
            conn.close()
        except Exception:
            pass


def safe_publish_event(queue_name: str, payload: Dict[str, Any]) -> None:
    """Publish and log outcome without raising."""
    ok = publish_json(queue_name, payload)
    if ok:
        logger.info(f"Published event to {queue_name}: {payload.get('type')}")
    else:
        logger.info(f"Skipped publishing event to {queue_name} (broker unavailable)")
