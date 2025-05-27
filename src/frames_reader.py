import cv2
import time
import threading
from logger import logger
from shared import batch_system_ctx, gpu

def camera_reader(camera_ctx):
    """单个摄像头读取线程"""
    while not camera_ctx.stop_event.is_set():
        if not camera_ctx.config["rtsp_url"]: 
            logger.error(f"摄像头 {camera_ctx.id} 配置错误: RTSP URL为空")
            time.sleep(10)  # 10s重连
            continue
        cap = cv2.VideoCapture(camera_ctx.config["rtsp_url"])
        try:
            while not camera_ctx.stop_event.is_set():
                ret, frame = cap.read()
                if not ret:
                    logger.warning(f"摄像头{camera_ctx.id}连接中断，尝试重连...")
                    break
                
                if camera_ctx.frame_queue.full():
                    continue
                
                if gpu:
                    batch_system_ctx.batch_queue.put((camera_ctx.id, frame))
                else:
                   camera_ctx.frame_queue.put(frame)
        finally:
            cap.release()
            logger.info(f"摄像头{camera_ctx.id}RTSP流已释放")
            time.sleep(camera_ctx.config["retry_interval"])
    
def start_readers(system_ctx):
    """启动所有摄像头读取线程"""
    return [
        threading.Thread(
            target=camera_reader, 
            args=(cam,),
            daemon=True,
            name=f"Reader-{cam.id}"
        ) for cam in system_ctx.cameras
    ]