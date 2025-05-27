import logging
import os
import time
import glob
from logging.handlers import RotatingFileHandler

class SmartRotatingFileHandler(RotatingFileHandler):
    def __init__(self, filename, maxBytes=0, backupCount=0, encoding=None, delay=False):
        self._original_filename = filename
        self._backup_count = backupCount
        self._max_bytes = maxBytes
        # 自动查找可用文件
        self._current_file = self._find_available_file()
        super().__init__(
            self._current_file,
            maxBytes=maxBytes,
            backupCount=backupCount,
            encoding=encoding,
            delay=delay
        )
        self._clean_old_logs()

    #  查找可用文件
    def _find_available_file(self):
        base, ext = os.path.splitext(self._original_filename)
        existing_files = glob.glob(f"{base}_*{ext}") + [self._original_filename]
        # 按修改时间排序
        valid_files = []
        for f in existing_files:
            if os.path.isfile(f):
                valid_files.append((f, os.path.getmtime(f)))
        if not valid_files:
            return self._generate_new_filename()  
        # 找到最新文件
        latest_file = max(valid_files, key=lambda x: x[1])[0]
        # 检查文件大小
        if os.path.getsize(latest_file) < self._max_bytes:
            return latest_file
        return self._generate_new_filename()

    #  时间戳命名文件
    def _generate_new_filename(self):
        base, ext = os.path.splitext(self._original_filename)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        return f"{base}_{timestamp}{ext}"

    # 清理旧文件
    def _clean_old_logs(self):
        base, ext = os.path.splitext(self._original_filename)
        log_files = glob.glob(f"{base}_*{ext}")
        # 按修改时间排序
        log_files.sort(key=os.path.getmtime)
        while len(log_files) > self._backup_count:
            oldest = log_files.pop(0)
            try:
                os.remove(oldest)
            except Exception as e:
                logging.error(f"删除旧日志失败: {e}")

    #  重写轮转逻辑
    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None
        # 生成新文件名
        new_name = self._generate_new_filename()
        self.baseFilename = new_name
        if not self.delay:
            self.stream = self._open()
        # 每次轮转后清理旧文件
        self._clean_old_logs()

#  设置日志记录器
def setup_logger(log_file='../log/rtsp.log', max_bytes=5*1024*1024, backup_count=3):
    log_dir = os.path.dirname(log_file)
    os.makedirs(log_dir, exist_ok=True)
    handler = SmartRotatingFileHandler(
        filename=log_file,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    # 日志格式
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(threadName)s: %(message)s'
    )
    handler.setFormatter(formatter)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    # 清除已有处理器
    for h in logger.handlers[:]:
        logger.removeHandler(h)
    logger.addHandler(handler)
    logger.info("APP 启动")

    return logger

#  初始化日志
logger = setup_logger()