import cv2
import time
import threading
import queue
from config_loader import load_config
from shared import frame_queue, stop_event
from logger import setup_logger

logger = setup_logger()
config = load_config("../config/config.json")
RTSP_URL = config["rtsp_url"]
RETRY_INTERVAL = config["retry_interval"]

def read_frames(stop_event):
    retry_interval = RETRY_INTERVAL
    while not stop_event.is_set():
        cap = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)
        if cap.isOpened():
            logger.info("成功连接到RTSP流,开始检测...")
            break
        else:
            logger.error(f"无法连接到RTSP流,将在 {retry_interval} 秒后重试...")
            time.sleep(retry_interval)

    try:
        while not stop_event.is_set():
            ret, frame = cap.read()
            if not ret or frame is None:
                logger.warning("读取帧失败，尝试重新连接...")
                cap.release()
                return read_frames(stop_event)

            if frame_queue.full():
                time.sleep(0.01)
                continue

            frame_queue.put(frame)
    except Exception as e:
        logger.exception(f"读取RTSP流时发生异常: {e}")
    finally:
        cap.release()
        logger.info("RTSP流已释放")