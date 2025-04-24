# config/logging_config.py
import logging
import sys
from pathlib import Path

def setup_logging(log_level=logging.INFO, log_file="logs/nl2sql_analyzer.log"): # <--- Check this line carefully
    """Configures logging to file and console."""
    log_dir = Path(log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True) # Ensure log directory exists

    log_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)-5.5s] [%(name)s] %(message)s"
    )
    root_logger = logging.getLogger()
    # ... (rest of the function) ...