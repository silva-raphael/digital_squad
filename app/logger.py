import sys
from datetime import datetime
from loguru import logger as _logger

# internal packages
from app.config import PROJECT_ROOT

_print_level = "INFO"

def define_log_level(print_level="DEBUG", logfile_level="DEBUG", name: str = None):
    """Adjust log level to level above"""
    global _print_level
    _print_level = print_level
    current_date = datetime.now()
    formatted_date = current_date.strftime("%Y/%m/%d%H%M%S")
    
    # Custom log format with special treatment for THOUGHT messages
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS zz}</green> | "
        "<level>{level: <8}</level> | "
        "<yellow>Line {line: >4} ({file}):</yellow> "
        "{message}\n"
    )
    
    # Special format for THOUGHT level - entire message in dark green
    thought_format = (
        "<magenta>{time:YYYY-MM-DD HH:mm:ss.SSS zz} | "
        "{level: <8} | "
        "Line {line: >4} ({file}): "
        "{message}</magenta>\n"
    )
    
    log_name = f"{name}_{formatted_date}" if name else formatted_date
    
    # possibility to name the log with a specific name
    _logger.remove()
    
    # Define a custom level
    _logger.level("THOUGHT", no=15, color="<magenta>")
    
    # Define the level with Loguru
    _logger.add(sys.stderr, level=print_level, format=lambda record: thought_format if record["level"].name == "THOUGHT" else log_format)
    _logger.add(PROJECT_ROOT / f"logs/{log_name}.log", level=logfile_level)
    
    return _logger

logger = define_log_level()

if __name__ == "__main__":
    logger.info("Info message")
    logger.debug("Debug message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")
    logger.log("THOUGHT", "Agent thought message")  # No need for extra tags since format handles it
    
    try:
        raise ValueError("Test error")
    except Exception as e:
        logger.exception(f"Exception message: {e}")