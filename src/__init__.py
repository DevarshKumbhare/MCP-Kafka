from .server import serve


def main():
    import argparse
    import asyncio
    import logging

    parser = argparse.ArgumentParser(
        description="Give a model the ability to interact with Apache Kafka"
    )
    # Kafka connection arguments
    parser.add_argument("--kafka-bootstrap-servers", type=str, required=True, help="Comma-separated list of Kafka bootstrap servers (e.g., 'localhost:9092')")
    parser.add_argument("--kafka-security-protocol", type=str, default="PLAINTEXT", help="Security protocol for Kafka connection (e.g., PLAINTEXT, SSL, SASL_PLAINTEXT, SASL_SSL)")
    parser.add_argument("--kafka-sasl-mechanism", type=str, help="SASL mechanism for Kafka authentication (e.g., PLAIN, SCRAM-SHA-256, SCRAM-SHA-512)")
    parser.add_argument("--kafka-sasl-plain-username", type=str, help="Username for SASL/PLAIN authentication")
    parser.add_argument("--kafka-sasl-plain-password", type=str, help="Password for SASL/PLAIN authentication")
    # Add arguments for other SASL mechanisms or SSL configuration if needed (e.g., ssl_cafile, ssl_certfile, ssl_keyfile)

    # Logging configuration (optional, but good practice)
    parser.add_argument("--log-level", type=str, default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], help="Set the logging level")

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('server.log'), # Keep logging to file
            logging.StreamHandler()         # Keep logging to console
        ]
    )
    logger = logging.getLogger("mcp-kafka")
    logger.info("Starting Kafka MCP Server...")
    logger.debug(f"Parsed arguments: {args}")


    # Prepare Kafka connection config dictionary
    kafka_config = {
        "bootstrap_servers": args.kafka_bootstrap_servers.split(","),
        "security_protocol": args.kafka_security_protocol,
        "sasl_mechanism": args.kafka_sasl_mechanism,
        "sasl_plain_username": args.kafka_sasl_plain_username,
        "sasl_plain_password": args.kafka_sasl_plain_password,
        # Add other relevant kafka-python config options based on args
    }
    # Filter out None values for cleaner config
    kafka_config = {k: v for k, v in kafka_config.items() if v is not None}

    # Validate SASL configuration
    if args.kafka_sasl_mechanism:
        if args.kafka_sasl_mechanism == "PLAIN":
            if not args.kafka_sasl_plain_username or not args.kafka_sasl_plain_password:
                parser.error("--kafka-sasl-plain-username and --kafka-sasl-plain-password are required when --kafka-sasl-mechanism is PLAIN")
        # Add validation for other SASL mechanisms if needed
        if not args.kafka_security_protocol.startswith("SASL_"):
            parser.error(f"--kafka-security-protocol must start with SASL_ when --kafka-sasl-mechanism ('{args.kafka_sasl_mechanism}') is set")
    elif args.kafka_security_protocol.startswith("SASL_"):
         parser.error("--kafka-sasl-mechanism must be provided when --kafka-security-protocol starts with SASL_")


    try:
        asyncio.run(serve(kafka_config=kafka_config))
    except KeyboardInterrupt:
        logger.info("Server stopped by user.")
    except Exception as e:
        logger.critical(f"Server encountered a critical error: {e}", exc_info=True)


if __name__ == "__main__":
    main()
