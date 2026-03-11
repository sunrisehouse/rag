import logging
import os
from logging.handlers import RotatingFileHandler

def get_logger(name):
    # 이미 해당 이름의 로거에 핸들러가 설정되어 있다면 그대로 반환 (중복 방지)
    logger = logging.getLogger(name)
    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.INFO)
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    # [%(module)s]와 [%(funcName)s]를 추가하여 상세 위치 파악
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(name)s] [%(module)s:%(funcName)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 콘솔 핸들러
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 파일 핸들러
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, "app.log"),
        maxBytes=5*1024*1024,
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger