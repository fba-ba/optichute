import logging
import sys


def setup_logger(log_level='INFO'):
    """
    Setup and configure logger.
    
    Args:
        log_level: Log level (DEBUG, INFO, WARNING, ERROR)
    
    Returns:
        Configured logger
    """
    # Convert string to logging level
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Configure root logger
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger('wood_optimizer')
