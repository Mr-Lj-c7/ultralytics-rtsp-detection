import queue
import threading
import numpy as np
import cv2
import time
from ultralytics import YOLO
from logger import logger
from shared import time_


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

def camera_processor(camera_ctx):
    """单摄像头处理线程"""
    model = YOLO(camera_ctx.config["model_path"])
    while not camera_ctx.stop_event.is_set():
        try:
            frame = camera_ctx.frame_queue.get(timeout=3)
            # start_time = time.time()
            time_.start('time_0')
            result_img, results = predict_and_detect(chosen_model=model, 
                                            img=frame, 
                                            classes=camera_ctx.config["target_classes"],  # define detect class
                                            conf=camera_ctx.config["confidence_threshold"],
                                            rectangle_thickness=camera_ctx.config["rectangle_thickness"],
                                            text_thickness=camera_ctx.config["text_thickness"])
            if results is not None:
                classes_ = [result.names[int(box.cls[0])] for result in results for box in result.boxes]
                # end_time = time.time()
                # logger.info(f"检测结果：{classes_}, 检测耗时：{(end_time-start_time)*1000:.2f}ms")
                logger.info(f"检测结果：{classes_}, 检测耗时：{(time_.end('time_0'))*1000:.2f}ms")
            camera_ctx.result_queue.put(result_img)
        except queue.Empty:
            continue
        except Exception as e:
            logger.error(f"帧处理错误: {e}", exc_info=True)   
    logger.info("模型处理RTSP流已释放")

def start_processors(system_ctx):
    """启动所有处理线程"""
    return [
        threading.Thread(
            target=camera_processor,
            args=(cam,),
            daemon=True,
            name=f"Processor-{cam.id}"
        ) for cam in system_ctx.cameras
    ]

def batch_processor(system_ctx, batch_size=4, timeout=0.1):
    """批量处理线程"""
    model = system_ctx.model
    while not system_ctx.global_stop.is_set():
        batch = []
        camera_ids = []
        start_time = time.time()
        # 收集足够数量的帧或超时
        while len(batch) < batch_size and (time.time() - start_time) < timeout:
            try:
                camera_id, frame = system_ctx.batch_queue.get(timeout=0.01)
                batch.append(frame)
                camera_ids.append(camera_id)
            except queue.Empty:
                continue     
        if len(batch) == 0:
            continue
        try:
            results = model.predict(batch, verbose=False)
        except Exception as e:
            logger.error(f"批量推理失败: {e}")
            continue
        # 处理并分发每个摄像头结果
        for idx, (camera_id, result) in enumerate(zip(camera_ids, results)):
            # 找到对应摄像头上下文
            cam = next(c for c in system_ctx.cameras if c.id == camera_id)     
            # 绘制检测框
            result_img = batch[idx].copy()
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cls = int(box.cls[0])
                cv2.rectangle(result_img, (x1, y1), (x2, y2), (255,0,0), 2)
                label = f"{result.names[cls]}"
                cv2.putText(result_img, label, (x1, y1-10), 
                           cv2.FONT_HERSHEY_PLAIN, 1, (0,0,255), 1) 
            cam.result_queue.put(result_img)