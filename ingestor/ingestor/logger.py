import logging
import os
from logging.handlers import RotatingFileHandler
from . import config

def setup_logging():
    """콘솔과 파일에 모두 로그를 남기도록 로거를 설정합니다."""
    log_dir = os.path.dirname(config.LOG_FILE_PATH)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logger = logging.getLogger("ingestor")
    logger.setLevel(config.LOG_LEVEL.upper())

    # 이미 핸들러가 설정되어 있는 경우 중복 추가 방지
    if logger.hasHandlers():
        return logger

    # 포맷터 설정
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # 콘솔 핸들러
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # 파일 핸들러 (Rotating)
    fh = RotatingFileHandler(
        config.LOG_FILE_PATH, maxBytes=10 * 1024 * 1024, backupCount=5
    )
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger

log = setup_logging()
