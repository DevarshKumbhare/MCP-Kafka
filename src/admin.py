import logging
from typing import Optional, List, Dict, Any
from kafka.admin import AIOKafkaAdminClient, NewTopic, TopicPartition
from kafka.errors import UnknownTopicOrPartitionError, TopicAlreadyExistsError

logger = logging.getLogger(__name__)

class RabbitMQAdmin:
    def __init__(self, host: str, port: int, username: str, password: str, use_tls: bool):
        self.protocol = "https" if use_tls else "http"
        self.base_url = f"{self.protocol}://{host}:{port}/api"
        self.auth = base64.b64encode(f"{username}:{password}".encode()).decode()
        self.headers = {
            "Authorization": f"Basic {self.auth}",
            "Content-Type": "application/json"
        }

    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> requests.Response:
        url = f"{self.base_url}/{endpoint}"
        response = requests.request(method, url, headers=self.headers, json=data, verify=True)
        response.raise_for_status()
        return response

    def list_queues(self) -> List[Dict]:
        """List all queues in the RabbitMQ server"""
        response = self._make_request("GET", "queues")
        return response.json()

    def list_exchanges(self) -> List[Dict]:
        """List all exchanges in the RabbitMQ server"""
        response = self._make_request("GET", "exchanges")
        return response.json()

    def get_queue_info(self, queue: str, vhost: str = "/") -> Dict:
        """Get detailed information about a specific queue"""
        vhost_encoded = requests.utils.quote(vhost, safe='')
        response = self._make_request("GET", f"queues/{vhost_encoded}/{queue}")
        return response.json()

    def delete_queue(self, queue: str, vhost: str = "/") -> None:
        """Delete a queue"""
        validate_rabbitmq_name(queue, "Queue name")
        vhost_encoded = requests.utils.quote(vhost, safe='')
        self._make_request("DELETE", f"queues/{vhost_encoded}/{queue}")

    def purge_queue(self, queue: str, vhost: str = "/") -> None:
        """Remove all messages from a queue"""
        validate_rabbitmq_name(queue, "Queue name")
        vhost_encoded = requests.utils.quote(vhost, safe='')
        self._make_request("DELETE", f"queues/{vhost_encoded}/{queue}/contents")

    def get_exchange_info(self, exchange: str, vhost: str = "/") -> Dict:
        """Get detailed information about a specific exchange"""
        vhost_encoded = requests.utils.quote(vhost, safe='')
        response = self._make_request("GET", f"exchanges/{vhost_encoded}/{exchange}")
        return response.json()

    def delete_exchange(self, exchange: str, vhost: str = "/") -> None:
        """Delete an exchange"""
        validate_rabbitmq_name(exchange, "Exchange name")
        vhost_encoded = requests.utils.quote(vhost, safe='')
        self._make_request("DELETE", f"exchanges/{vhost_encoded}/{exchange}")

    def get_bindings(self, queue: Optional[str] = None, exchange: Optional[str] = None, vhost: str = "/") -> List[Dict]:
        """Get bindings, optionally filtered by queue or exchange"""
        vhost_encoded = requests.utils.quote(vhost, safe='')
        if queue:
            validate_rabbitmq_name(queue, "Queue name")
            response = self._make_request("GET", f"queues/{vhost_encoded}/{queue}/bindings")
        elif exchange:
            validate_rabbitmq_name(exchange, "Exchange name")
            response = self._make_request("GET", f"exchanges/{vhost_encoded}/{exchange}/bindings/source")
        else:
            response = self._make_request("GET", f"bindings/{vhost_encoded}")
        return response.json()

    def get_overview(self) -> Dict:
        """Get overview of RabbitMQ server including version, stats, and listeners"""
        response = self._make_request("GET", "overview")
        return response.json()

async def handle_get_topic_info(admin_client: AIOKafkaAdminClient, topic: str) -> Dict[str, Any]:
    """Gets detailed information about a specific Kafka topic."""
    logger.info(f"Fetching information for topic '{topic}'...")
    try:
        # describe_topics returns a list, even for a single topic
        topic_metadata_list = await admin_client.describe_topics([topic])
        if not topic_metadata_list:
            raise UnknownTopicOrPartitionError(f"Topic '{topic}' not found.")

        # Extract the metadata for the requested topic
        topic_metadata = topic_metadata_list[0]

        # Describe configs for the topic
        config_desc = await admin_client.describe_configs(resource_configs=[('topic', topic)])
        topic_config = config_desc[0]['configs'] if config_desc else {}

        # Get consumer group information related to the topic (optional, can be complex)
        # groups = await admin_client.list_consumer_groups()
        # topic_groups = []
        # for group_id, _ in groups:
        #     try:
        #         group_desc = await admin_client.describe_consumer_groups([group_id])
        #         if group_desc and group_desc[0]['state'] != 'Dead':
        #             # Check if group consumes the topic (requires offset fetching)
        #             # This part can be involved and might require listing/fetching offsets
        #             pass # Simplified for now
        #     except Exception as group_err:
        #         logger.warning(f"Could not describe group '{group_id}': {group_err}")

        result = {
            "topic_name": topic_metadata['topic'],
            "is_internal": topic_metadata['is_internal'],
            "partitions": [
                {
                    "partition_id": p_meta['partition'],
                    "leader": p_meta['leader'],
                    "replicas": p_meta['replicas'],
                    "isr": p_meta['isr'],
                    # Add partition offset info if needed (requires consumer API)
                }
                for p_meta in topic_metadata['partitions']
            ],
            "configuration": topic_config,
            # "consumer_groups": topic_groups # Add if implemented
        }
        logger.info(f"Successfully fetched information for topic '{topic}'.")
        return result
    except UnknownTopicOrPartitionError as e:
         logger.warning(f"Topic '{topic}' not found.")
         raise e # Re-raise to be handled by the server
    except Exception as e:
        logger.error(f"Failed to get information for topic '{topic}': {e}", exc_info=True)
        raise

async def handle_delete_topic(admin_client: AIOKafkaAdminClient, topic: str) -> None:
    """Deletes a Kafka topic."""
    logger.info(f"Attempting to delete topic '{topic}'...")
    try:
        await admin_client.delete_topics(topics=[topic], timeout_ms=30000) # 30 second timeout
        logger.info(f"Successfully submitted deletion request for topic '{topic}'. Note: Deletion might take time on the broker.")
    except UnknownTopicOrPartitionError:
         logger.warning(f"Cannot delete topic '{topic}': Topic not found.")
         raise # Re-raise to inform the user
    except Exception as e:
        # Add more specific error handling if needed (e.g., PolicyViolationError)
        logger.error(f"Failed to delete topic '{topic}': {e}", exc_info=True)
        raise

async def handle_create_topic(
    admin_client: AIOKafkaAdminClient,
    topic: str,
    num_partitions: int = 1,
    replication_factor: int = 1,
    config: Optional[Dict[str, str]] = None
) -> None:
    """Creates a new Kafka topic."""
    logger.info(f"Attempting to create topic '{topic}' with {num_partitions} partitions and replication factor {replication_factor}...")
    new_topic = NewTopic(
        name=topic,
        num_partitions=num_partitions,
        replication_factor=replication_factor,
        topic_configs=config or {}
    )
    try:
        await admin_client.create_topics(new_topics=[new_topic], validate_only=False)
        logger.info(f"Successfully created topic '{topic}'.")
    except TopicAlreadyExistsError:
        logger.warning(f"Topic '{topic}' already exists.")
        # Decide if this should be an error or just a warning
        # raise # Uncomment to make it an error
    except Exception as e:
        # Add more specific error handling (e.g., PolicyViolationError, InvalidReplicationFactorError)
        logger.error(f"Failed to create topic '{topic}': {e}", exc_info=True)
        raise

# Add other admin functions as needed (e.g., handle_alter_topic_config)
