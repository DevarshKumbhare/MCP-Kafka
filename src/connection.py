import logging
from contextlib import asynccontextmanager
from kafka.admin import AIOKafkaAdminClient
from kafka.producer import AIOKafkaProducer
from kafka.errors import KafkaConnectionError

logger = logging.getLogger(__name__)

@asynccontextmanager
async def get_kafka_producer(config: dict):
    """Provides an asynchronous Kafka producer within an async context manager."""
    producer = AIOKafkaProducer(**config)
    try:
        logger.info("Starting Kafka producer...")
        await producer.start()
        logger.info("Kafka producer started successfully.")
        yield producer
    except KafkaConnectionError as e:
        logger.error(f"Failed to connect Kafka producer: {e}")
        raise # Re-raise the specific connection error
    except Exception as e:
        logger.error(f"Error during Kafka producer operation: {e}", exc_info=True)
        raise # Re-raise other exceptions
    finally:
        logger.info("Stopping Kafka producer...")
        await producer.stop()
        logger.info("Kafka producer stopped.")

@asynccontextmanager
async def get_kafka_admin_client(config: dict):
    """Provides an asynchronous Kafka admin client within an async context manager."""
    admin_client = AIOKafkaAdminClient(**config)
    try:
        logger.info("Starting Kafka admin client...")
        await admin_client.start()
        logger.info("Kafka admin client started successfully.")
        yield admin_client
    except KafkaConnectionError as e:
        logger.error(f"Failed to connect Kafka admin client: {e}")
        raise
    except Exception as e:
        logger.error(f"Error during Kafka admin client operation: {e}", exc_info=True)
        raise
    finally:
        logger.info("Stopping Kafka admin client...")
        await admin_client.close()
        logger.info("Kafka admin client stopped.")

# We might add a consumer context manager later if needed for consume tools
# @asynccontextmanager
# async def get_kafka_consumer(config: dict, topics: list[str]):
#     consumer = AIOKafkaConsumer(*topics, **config)
#     try:
#         logger.info(f"Starting Kafka consumer for topics: {topics}...")
#         await consumer.start()
#         logger.info("Kafka consumer started successfully.")
#         yield consumer
#     except KafkaConnectionError as e:
#         logger.error(f"Failed to connect Kafka consumer: {e}")
#         raise
#     except Exception as e:
#         logger.error(f"Error during Kafka consumer operation: {e}", exc_info=True)
#         raise
#     finally:
#         logger.info("Stopping Kafka consumer...")
#         await consumer.stop()
#         logger.info("Kafka consumer stopped.")

# Removed validate_rabbitmq_name function
