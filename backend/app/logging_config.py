"""
Logging configuration for IntelliGrid backend.
"""
import logging
import sys

def setup_logging():
    """Configure logging for production."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Reduce noise from external libraries
    logging.getLogger('uvicorn').setLevel(logging.WARNING)
    logging.getLogger('fastapi').setLevel(logging.WARNING)
    
    return logging.getLogger('intelligrid')

logger = setup_logging()
