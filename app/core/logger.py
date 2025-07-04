import os
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler

def get_logger(name: str = __name__) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:  # hanya setup sekali
        # Base dir: naik 3 level dari file ini
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        log_dir = os.path.join(BASE_DIR, "logs")
        os.makedirs(log_dir, exist_ok=True)

        # Buat nama file log baru berdasarkan timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file_path = os.path.join(log_dir, f"app_{timestamp}.log")

        # Setup RotatingFileHandler (opsional: tetap batasi ukuran log per run)
        rotating_handler = RotatingFileHandler(
            filename=log_file_path,
            mode='a',
            maxBytes=1 * 1024 * 1024,  # 1MB per file
            backupCount=5,             # simpan sampai app_xxx.log.5
            encoding='utf-8',
            delay=False
        )

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )
        rotating_handler.setFormatter(formatter)

        logger.setLevel(logging.DEBUG)
        logger.addHandler(rotating_handler)

        # Optional: tampilkan juga di console
        # console_handler = logging.StreamHandler()
        # console_handler.setFormatter(formatter)
        # logger.addHandler(console_handler)

    return logger