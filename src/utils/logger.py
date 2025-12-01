import logging
import sys
import structlog
from pathlib import Path

def configure_logger(log_dir: str = "logs", log_level: str = "INFO"):
    """
    Configure structlog and standard logging.
    
    Args:
        log_dir: Directory to store log files.
        log_level: Logging level (INFO, DEBUG, etc.).
    """
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    # Configure standard logging
    # We remove existing handlers to avoid duplication if called multiple times
    root_logger = logging.getLogger()
    if root_logger.handlers:
        for handler in root_logger.handlers:
            root_logger.removeHandler(handler)
            
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper())
    )
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Add file handler
    file_handler = logging.FileHandler(f"{log_dir}/autosub.log", encoding="utf-8")
    file_handler.setFormatter(logging.Formatter('%(message)s'))
    root_logger.addHandler(file_handler)

def get_logger(name: str):
    """Get a structlog logger."""
    return structlog.get_logger(name)
