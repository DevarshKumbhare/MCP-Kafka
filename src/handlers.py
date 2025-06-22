from .connection import RabbitMQConnection
from .admin import RabbitMQAdmin
from typing import List, Optional, Any
import logging
from kafka.producer import AIOKafkaProducer
from kafka.admin import AIOKafkaAdminClient

logger = logging.getLogger(__name__)

def handle_enqueue(rabbitmq: RabbitMQConnection, queue: str, message: str):
    connection, channel = rabbitmq.get_channel()
    channel.queue_declare(queue)
    channel.basic_publish(exchange="", routing_key=queue, body=message)
    connection.close()

def handle_fanout(rabbitmq: RabbitMQConnection, exchange: str, message: str):
    connection, channel = rabbitmq.get_channel()
    channel.exchange_declare(exchange=exchange, exchange_type="fanout")
    channel.basic_publish(exchange=exchange, routing_key="", body=message)
    connection.close()

def handle_list_queues(rabbitmq_admin: RabbitMQAdmin) -> List[str]:
    result = rabbitmq_admin.list_queues()
    return [queue['name'] for queue in result]

def handle_list_exchanges(rabbitmq_admin: RabbitMQAdmin) -> List[str]:
    result = rabbitmq_admin.list_exchanges()
    return [exchange['name'] for exchange in result]

def handle_get_queue_info(rabbitmq_admin: RabbitMQAdmin, queue: str, vhost: str = "/") -> dict:
    return rabbitmq_admin.get_queue_info(queue, vhost)

def handle_delete_queue(rabbitmq_admin: RabbitMQAdmin, queue: str, vhost: str = "/") -> None:
    rabbitmq_admin.delete_queue(queue, vhost)

def handle_purge_queue(rabbitmq_admin: RabbitMQAdmin, queue: str, vhost: str = "/") -> None:
    rabbitmq_admin.purge_queue(queue, vhost)

def handle_delete_exchange(rabbitmq_admin: RabbitMQAdmin, exchange: str, vhost: str = "/") -> None:
    rabbitmq_admin.delete_exchange(exchange, vhost)

def handle_get_exchange_info(rabbitmq_admin: RabbitMQAdmin, exchange: str, vhost: str = "/") -> dict:
    return rabbitmq_admin.get_exchange_info(exchange, vhost)

async def handle_publish_message(producer: AIOKafkaProducer, topic: str, message: str, key: Optional[str] = None):
    """Publishes a message to a Kafka topic."""
    logger.info(f"Publishing message to topic '{topic}'...")
    try:
        # Encode message and key (if provided) to bytes
        message_bytes = message.encode('utf-8')
        key_bytes = key.encode('utf-8') if key else None

        await producer.send_and_wait(topic, value=message_bytes, key=key_bytes)
        logger.info(f"Message successfully published to topic '{topic}'.")
    except Exception as e:
        logger.error(f"Failed to publish message to topic '{topic}': {e}", exc_info=True)
        raise # Re-raise the exception to be caught in server.py

async def handle_list_topics(admin_client: AIOKafkaAdminClient) -> List[str]:
    """Lists all available topics in the Kafka cluster."""
    logger.info("Fetching list of Kafka topics...")
    try:
        topics = await admin_client.list_topics()
        logger.info(f"Successfully fetched {len(topics)} topics.")
        return topics
    except Exception as e:
        logger.error(f"Failed to list Kafka topics: {e}", exc_info=True)
        raise

# Placeholder for other handlers (like consume, describe topic, etc.)
# We will need corresponding admin functions in admin.py for some of these

# Example:
# async def handle_consume_messages(consumer: AIOKafkaConsumer, max_messages: int = 10, timeout_ms: int = 1000):
#     """Consumes messages from the subscribed topics."""
#     logger.info(f"Consuming messages...")
#     messages = []
#     try:
#         async for msg in consumer:
#             messages.append({
#                 "topic": msg.topic,
#                 "partition": msg.partition,
#                 "offset": msg.offset,
#                 "key": msg.key.decode('utf-8') if msg.key else None,
#                 "value": msg.value.decode('utf-8') # Assuming utf-8 encoded messages
#             })
#             if len(messages) >= max_messages:
#                 break
#         # Potentially add a timeout mechanism if no messages arrive
#         logger.info(f"Consumed {len(messages)} messages.")
#         return messages
#     except Exception as e:
#         logger.error(f"Failed to consume messages: {e}", exc_info=True)
#         raise
