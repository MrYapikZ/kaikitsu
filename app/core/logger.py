import logging

# Configure root logger
logging.basicConfig(
    level=logging.INFO,  # or logging.DEBUG for more verbosity
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler()  # Output to console
        # You can also add FileHandler if needed
    ]
)

def get_logger(name: str = __name__) -> logging.Logger:
    return logging.getLogger(name)