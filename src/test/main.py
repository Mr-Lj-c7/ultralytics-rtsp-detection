import os
print(os.getcwd())

import threading
import logging
import time
from logger import setup_logger
from frames_reader import read_frames
from frames_process import process_frames
from show import display_results
from web_show import run_webserver
from shared import stop_event

# 初始化日志
logger = setup_logger()

def main():
    # 创建线程
    reader_thread = threading.Thread(target=read_frames, args=(stop_event,), daemon=True, name="RTSPReader")
    processor_thread = threading.Thread(target=process_frames, args=(stop_event,), daemon=True, name="FrameProcessor")
    # display_thread = threading.Thread(target=display_results, args=(stop_event,), daemon=True, name="DisplayThread")  #  本地显示结果
    webserver_thread = threading.Thread(target=run_webserver, daemon=True, name="WebServer")  #  web端显示结果

    # 启动线程
    # threads = [reader_thread, processor_thread, display_thread, webserver_thread]
    threads = [reader_thread, processor_thread, webserver_thread]

    try:
        for t in threads:
            t.start()
        
        # 主线程保持运行
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("收到终止信号，清理资源...")
        stop_event.set()
        for t in threads:
            t.join(timeout=1)
    finally:
        logger.info("系统安全退出")

if __name__ == "__main__":
    main()