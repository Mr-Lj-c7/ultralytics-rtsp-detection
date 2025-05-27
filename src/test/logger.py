import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger(log_file='./log/rtsp.log', max_bytes=5 * 1024 * 1024, backup_count=3):
    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    headler = RotatingFileHandler(
        log_file, 
        maxBytes=max_bytes, 
        backupCount=backup_count)
    
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(threadName)s: %(message)s'
    )
    headler.setFormatter(formatter)

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.addHandler(headler)
    logger.info("APP启动")

    return logger