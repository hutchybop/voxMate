# Required local import
from utils.logging import logger


def cleanup() -> None:
    """Cleanup resources before exit"""
    if hasattr(cleanup, '_called'):
        return
    cleanup._called = True
    logger.info("Performing cleanup...")
    # Add any additional cleanup needed here