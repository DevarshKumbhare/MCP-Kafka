from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    TextContent,
    Tool,
)
import logging
# Removed RabbitMQ imports
# from .connection import RabbitMQConnection, validate_rabbitmq_name
# from .handlers import (
#     handle_enqueue,
#     handle_fanout,
#     handle_list_queues,
#     handle_list_exchanges,
#     handle_get_queue_info,
#     handle_delete_queue,
#     handle_purge_queue,
#     handle_delete_exchange,
#     handle_get_exchange_info
# )
# from .admin import RabbitMQAdmin

# Import Kafka handlers and admin (will be created later)
from .handlers import (
    handle_publish_message,
    handle_list_topics
    # Add other Kafka handlers here as needed
)
from .admin import (
    handle_get_topic_info,
    handle_delete_topic,
    # Add other Kafka admin handlers here
)

# Import Kafka connection management (will be created later)
from .connection import get_kafka_producer, get_kafka_admin_client # Assuming these helper functions

from .tools import MCP_TOOLS # We will update tools.py later

# Updated function signature to accept kafka_config dictionary
async def serve(kafka_config: dict) -> None:
    # Setup server with new name
    server = Server("mcp-kafka")
    # Get logger configured in __init__.py
    logger = logging.getLogger("mcp-kafka")
    # Removed logger setup from here

    # Kafka clients will be created within call_tool as needed,
    # or potentially managed globally if frequent reuse is expected.
    # We might need to handle their lifecycle (creation/closing).

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return MCP_TOOLS # Will be updated for Kafka

    @server.call_tool()
    async def call_tool(
        name: str,
        arguments: dict
    ) -> list[TextContent]:
        logger.debug(f"Executing tool: {name} with arguments: {arguments}")
        try:
            # Initialize Kafka clients based on the tool being called
            # Note: Consider optimizing client creation/reuse
            if name == "publish_message":
                topic = arguments["topic"]
                message = arguments["message"]
                key = arguments.get("key") # Optional message key
                # Kafka topic names have fewer restrictions than RabbitMQ queues/exchanges
                # We might add basic validation if needed (e.g., not empty)

                async with get_kafka_producer(kafka_config) as producer:
                    await handle_publish_message(producer, topic, message, key)
                return [TextContent(type="text", text="Message published successfully.")]

            elif name == "list_topics":
                async with get_kafka_admin_client(kafka_config) as admin_client:
                    result = await handle_list_topics(admin_client)
                return [TextContent(type="text", text=str(result))] # Format appropriately

            elif name == "get_topic_info":
                 async with get_kafka_admin_client(kafka_config) as admin_client:
                    topic = arguments["topic"]
                    result = await handle_get_topic_info(admin_client, topic)
                 return [TextContent(type="text", text=str(result))] # Format appropriately

            elif name == "delete_topic":
                 async with get_kafka_admin_client(kafka_config) as admin_client:
                    topic = arguments["topic"]
                    await handle_delete_topic(admin_client, topic)
                 return [TextContent(type="text", text=f"Topic '{topic}' deleted successfully.")]

            # Add more elif blocks for other Kafka tools (e.g., consume_messages, create_topic)

            else:
                 logger.error(f"Tool not found: {name}")
                 raise ValueError(f"Tool not found: {name}")

        except Exception as e:
            logger.error(f"Error executing tool '{name}': {e}", exc_info=True) # Log traceback
            # Provide a user-friendly error message
            return [TextContent(type="text", text=f"Failed to execute tool '{name}': {type(e).__name__} - {e}")]


    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        # Pass the initialized logger to the server run method if supported/needed
        # Otherwise, rely on the global logger configuration
        await server.run(read_stream, write_stream, options, raise_exceptions=False) # Set raise_exceptions=False to handle errors gracefully in call_tool
