import queue
import os
import time
import threading
from ultralytics import YOLO
from config_loader import load_config
from logger import logger

gpsu = os.environ.get("GPU", "0")
gpu = gpsu == "1"

class Timer:
    def __init__(self):
        self.start_times = {}
        self.lock = threading.Lock()

    def start(self, name):
        with self.lock:
            self.start_times[name] = time.time()

    def end(self, name):
        with self.lock:
            start_time = self.start_times.pop(name, None)
            if start_time is None:
                logger.warning(f"计时器 '{name}' 未被正确初始化")
                return 0.0
            return time.time() - start_time

#  摄像头配置
class CameraContext:
    def __init__(self, camera_config, global_config):
        self.last_update = time.time()
        self.status = "init"
        self.id = camera_config["id"]
        self.frame_queue = queue.Queue(maxsize=global_config["queue_maxsize"])
        self.result_queue = queue.Queue(maxsize=30)
        self.stop_event = threading.Event()
        self.config = {
            **camera_config,
            **global_config
        }

#  batch_size = 1
class SystemContext:
    def __init__(self, config):
        self.global_stop = threading.Event()
        self.cameras = [
            CameraContext(cam, config["global"]) 
            for cam in config["cameras"]
        ]

#  batch_size > 1
class BatchSystemContext:
    def __init__(self, config):
        self.global_stop = threading.Event()
        self.cameras = [
            CameraContext(cam, config["global"]) 
            for cam in config["cameras"]
        ]
        #  加载模型
        model_path = {cam.config["model_path"] for cam in self.cameras}
        if (len(model_path) != 1):
            logger.error("模型路径不一致,批量推理要求所有摄像头使用相同模型")
            raise ValueError("模型路径不一致,批量推理要求所有摄像头使用相同模型")
        self.modle = YOLO(list(model_path)[0])
        # 批量处理队列（元组（camera_id, frame)）
        self.batch_queue = queue.Queue(maxsize=config["global"]["batch_queue_maxsize"])



#  加载配置
config = load_config("../config/config.json")
system_ctx = SystemContext(config)
batch_system_ctx = BatchSystemContext(config)
# 计时器
time_ = Timer()