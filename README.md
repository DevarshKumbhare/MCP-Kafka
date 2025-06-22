# Kafka MCP Server

A [Model Context Protocol](https://www.anthropic.com/news/model-context-protocol) server implementation for Apache Kafka. Enabling MCP client to interact with topics hosted in a Kafka instance.

## Running locally with the Claude desktop app

### Manual Installation
1. Clone this repository.
2. Add the following to your `claude_desktop_config.json` file:
- On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
- On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

```
{
    "mcpServers": {
      "kafka": {
        "command": "uv",
        "args": [
            "--directory",
            "/path/to/repo/mcp-kafka",
            "run",
            "mcp-server-kafka",
            "--kafka-bootstrap-servers",
            "<comma_separated_bootstrap_servers ex. localhost:9092,otherhost:9092>",
            # Add other Kafka connection arguments as needed (e.g., security protocol, SASL mechanism, username, password)
            # Example for SASL_SSL:
            # "--kafka-security-protocol", "SASL_SSL",
            # "--kafka-sasl-mechanism", "PLAIN",
            # "--kafka-sasl-plain-username", "<your_username>",
            # "--kafka-sasl-plain-password", "<your_password>"
        ]
      }
    }
}
```
4. Install and open the [Claude desktop app](https://claude.ai/download).
5. Try asking Claude to do a read/write operation of some sort to confirm the setup (e.g. ask it to publish a message to a topic or read messages from a topic). If there are issues, use the Debugging tools provided in the MCP documentation [here](https://modelcontextprotocol.io/docs/tools/debugging).
