import cv2
import time
import threading
from config_loader import load_config
from shared import result_queue
from logger import setup_logger

logger = setup_logger()
config = load_config("../config/config.json")
WINDOW_NAME = config["display_window_name"]

def display_results(stop_event):
    try:
        while not stop_event.is_set():
            if not result_queue.empty():
                result_img = result_queue.get()
                cv2.imshow(WINDOW_NAME, result_img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                logger.info("用户请求退出,准备终止所有线程...")
                stop_event.set()
                break
    except Exception as e:
        logger.error(f"显示线程发生异常: {e}", exc_info=True)
    finally:
        cv2.destroyAllWindows()
        logger.info("OpenCV 窗口已关闭")

