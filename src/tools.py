from .models import (
    PublishMessage,
    ListTopics,
    GetTopicInfo,
    DeleteTopic,
    CreateTopic
    # Add other Kafka models here if implemented
)
from mcp.types import (
    Tool,
)


MCP_TOOLS = [
    Tool(
        name="publish_message",
        description="Publish a message to a Kafka topic.",
        inputSchema=PublishMessage.model_json_schema(),
    ),
    Tool(
        name="list_topics",
        description="List all available topics in the Kafka cluster.",
        inputSchema=ListTopics.model_json_schema(),
    ),
    Tool(
        name="get_topic_info",
        description="Get detailed information about a specific Kafka topic.",
        inputSchema=GetTopicInfo.model_json_schema(),
    ),
    Tool(
        name="delete_topic",
        description="Delete a specific Kafka topic.",
        inputSchema=DeleteTopic.model_json_schema(),
    ),
    Tool(
        name="create_topic",
        description="Create a new Kafka topic.",
        inputSchema=CreateTopic.model_json_schema(),
    ),
    # Add definitions for other Kafka tools here (e.g., consume_messages)
]

# Removed MCP_TOOL_ROUTING as it was empty/unused in the original