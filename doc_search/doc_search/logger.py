import logging
from logging.handlers import RotatingFileHandler
from . import config

# 로거 설정
log = logging.getLogger('doc_search')
log.setLevel(config.LOG_LEVEL)

# 파일 핸들러 설정
file_handler = RotatingFileHandler(
    config.LOG_FILE_PATH,
    maxBytes=10*1024*1024,  # 10 MB
    backupCount=5,
    encoding='utf-8'
)

# 포매터 설정
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# 핸들러 추가 (중복 방지)
if not log.handlers:
    log.addHandler(file_handler)

    # 콘솔 핸들러 추가
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    log.addHandler(console_handler)
