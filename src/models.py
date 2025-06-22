from typing import Annotated, Optional, Dict
from pydantic import BaseModel, Field

# Models for Kafka MCP Tools

class PublishMessage(BaseModel):
    topic: str = Field(..., description="The Kafka topic to publish the message to.")
    message: str = Field(..., description="The message content to publish.")
    key: Optional[str] = Field(None, description="Optional message key for partitioning.")

class ListTopics(BaseModel):
    # No arguments needed for listing topics
    pass

class GetTopicInfo(BaseModel):
    topic: str = Field(..., description="The name of the Kafka topic to get information about.")

class DeleteTopic(BaseModel):
    topic: str = Field(..., description="The name of the Kafka topic to delete.")

class CreateTopic(BaseModel):
    topic: str = Field(..., description="The name of the new Kafka topic to create.")
    num_partitions: int = Field(1, description="Number of partitions for the new topic.", gt=0)
    replication_factor: int = Field(1, description="Replication factor for the new topic.", gt=0)
    config: Optional[Dict[str, str]] = Field(None, description="Optional topic-level configurations (e.g., 'retention.ms').")

# Add models for other tools like ConsumeMessages if implemented
# class ConsumeMessages(BaseModel):
#     topic: str = Field(..., description="The Kafka topic to consume messages from.")
#     group_id: Optional[str] = Field(None, description="Consumer group ID. If None, a random group ID might be used.")
#     max_messages: int = Field(10, description="Maximum number of messages to consume.", gt=0)
#     timeout_ms: int = Field(5000, description="Time in milliseconds to wait for messages.")

# Remove original RabbitMQ models
# class Enqueue(BaseModel):
#     queue: str
#     message: str

# class Fanout(BaseModel):
#     exchange: str
#     message: str

# class ListQueues(BaseModel):
#     pass

# class ListExchanges(BaseModel):
#     pass

# class GetQueueInfo(BaseModel):
#     queue: str
#     vhost: Optional[str] = "/"

# class DeleteQueue(BaseModel):
#     queue: str
#     vhost: Optional[str] = "/"

# class PurgeQueue(BaseModel):
#     queue: str
#     vhost: Optional[str] = "/"

# class DeleteExchange(BaseModel):
#     exchange: str
#     vhost: Optional[str] = "/"

# class GetExchangeInfo(BaseModel):
#     exchange: str
#     vhost: Optional[str] = "/"
