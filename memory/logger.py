import logging

def get_master_logger():
    # Get or create the 'QuantBot' logger
    logger = logging.getLogger('QuantBot')

    # Check if handlers already exist to avoid duplicate logs
    if not logger.handlers:
        logger.setLevel(logging.INFO)

        # Create console handler
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
