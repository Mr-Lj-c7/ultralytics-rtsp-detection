import cv2
import time
from flask import Flask, Response, render_template
from logger import logger
from shared import system_ctx

app = Flask(__name__)

def generate_frames(camera):
    """视频流生成器"""
    while not camera.stop_event.is_set():
        try:
            if not camera.result_queue.empty():
                frame = camera.result_queue.get()
                
                # 编码帧为JPEG格式
                (success, encoded_image) = cv2.imencode(".jpg", frame)
                if not success:
                    continue
                
                frame_data = (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' 
                       + bytearray(encoded_image)
                       + b'\r\n')
                yield frame_data
            else:
                time.sleep(0.01)  # 避免CPU满载
        except Exception as e:
            logger.error(f"视频流生成异常: {e}")
            break

@app.route('/')
def index():
    """动态生成多画面页面"""
    return render_template('multi_cam.html', 
                         cameras=system_ctx.cameras)

@app.route('/video_feed/<camera_id>')
def video_feed(camera_id):
    """动态视频流路由"""
    camera = next(c for c in system_ctx.cameras if c.id == camera_id)
    return Response(generate_frames(camera),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

def run_webserver():
    """运行Flask服务器"""
    app.run(host='0.0.0.0', port=5000, threaded=True, use_reloader=False)
