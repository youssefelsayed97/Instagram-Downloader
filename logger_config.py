import sys
import logging


def setup_logger() -> logging.Logger:

    logger = logging.getLogger("App")

    if not logger.handlers:

        logger.setLevel(logging.INFO)

        console_handler = logging.StreamHandler(sys.stdout)
        file_handler = logging.FileHandler("app.log", encoding="utf-8")

        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger
