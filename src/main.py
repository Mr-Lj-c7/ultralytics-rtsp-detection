import os
print(os.getcwd())

import threading
import time
from logger import logger
from frames_reader import start_readers
from frames_process import start_processors, batch_processor
from web_show import run_webserver
from shared import system_ctx, batch_system_ctx, gpu

def main():
    # 创建所有线程
    if gpu:
        logger.info("使用GPU进行批量推理")
        threads = (
            start_readers(system_ctx) +
            [threading.Thread(target=batch_processor, args=(batch_system_ctx, 4), daemon=True, name="WebServer")] +
            [threading.Thread(target=run_webserver, daemon=True, name="WebServer")]
        ) 
    else:
        logger.info("使用CPU进行推理")
        threads = (
            start_readers(system_ctx) +
            start_processors(system_ctx) +
            [threading.Thread(target=run_webserver, daemon=True, name="WebServer")]
        )
    try:
        for t in threads:
            t.start()
        
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("收到终止信号，清理资源...")
        system_ctx.global_stop.set()
        for cam in system_ctx.cameras:
            cam.stop_event.set()
        
        for t in threads:
            t.join(timeout=1)
    finally:
        logger.info("系统安全退出")

if __name__ == "__main__":
    main()