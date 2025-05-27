import queue
import threading
import numpy as np
import cv2
from ultralytics import YOLO
from config_loader import load_config
from logger import setup_logger
from shared import frame_queue, result_queue

logger = setup_logger()
config = load_config("../config/config.json")
CONFIDENCE_THRESHOLD = config["confidence_threshold"]
RECTANGLE_THICKNESS = config["rectangle_thickness"]
TEXT_THICKNESS = config["text_thickness"]
WINDOW_NAME = config["display_window_name"]
TARGET_CLASSES = config["target_classes"]

model = YOLO(config["model_path"])

def predict(chosen_model, img, classes=None, conf=0.5):  # classes=None is all classes
    if classes is None:
        classes = []

    kwargs = {"conf": conf}
    if classes:
        kwargs["classes"] = classes

    try:
        results = chosen_model.predict(img, **kwargs)
    except Exception as e:
        logger.error(f"模型预测失败: {e}", exc_info=True)
        raise RuntimeError(f"模型预测失败: {e}") from e
        

    return results

def predict_and_detect(chosen_model, img, classes=[], conf=0.5, rectangle_thickness=2, text_thickness=1):
    results = predict(chosen_model, img, classes, conf=conf)
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cls = int(box.cls[0])

            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), rectangle_thickness)
            label = f"{result.names[cls]}"
            cv2.putText(img, label, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), text_thickness)
    return img, results

def process_frames(stop_event):
    while not stop_event.is_set():
        try:
            frame = frame_queue.get(timeout=3)
            result_img, _ = predict_and_detect(chosen_model=model, 
                                               img=frame, 
                                               classes=TARGET_CLASSES,  # define detect class
                                               conf=CONFIDENCE_THRESHOLD,
                                               rectangle_thickness=RECTANGLE_THICKNESS,
                                               text_thickness=TEXT_THICKNESS)
            result_queue.put(result_img)
        except queue.Empty:
            continue
        except Exception as e:
            logger.error(f"帧处理错误: {e}", exc_info=True)
        
    logger.info("模型处理RTSP流已释放")