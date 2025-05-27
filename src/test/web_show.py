import cv2
from flask import Flask, Response, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import time
import threading
from config_loader import load_config
from shared import result_queue, stop_event
from logger import setup_logger

logger = setup_logger()
config = load_config("../config/config.json")

app = Flask(__name__)

def generate_frames(stop_event):
    """视频流生成器"""
    while not stop_event.is_set():
        try:
            if not result_queue.empty():
                frame = result_queue.get()
                
                # 编码帧为JPEG格式
                (success, encoded_image) = cv2.imencode(".jpg", frame)
                if not success:
                    continue
                
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' 
                       + bytearray(encoded_image) + b'\r\n')
            else:
                time.sleep(0.01)  # 避免CPU满载
        except Exception as e:
            logger.error(f"视频流生成异常: {e}")
            stop_event.set()
            break

@app.route('/')
def index():
    """视频展示页面"""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """视频流路由"""
    return Response(generate_frames(stop_event=threading.Event()),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

def run_webserver():
    """运行Flask服务器"""
    app.run(host='0.0.0.0', port=5000, threaded=True, use_reloader=False)

@app.route('/api/control', methods=['POST'])
def control():
    """控制接口"""
    action = request.json.get('action')
    
    if action == 'start':
        stop_event.clear()
        logger.info("系统启动")
        return jsonify({'status': 'running'})
    
    elif action == 'stop':
        stop_event.set()
        logger.info("系统停止")
        return jsonify({'status': 'stopped'})
    
    return jsonify({'error': 'invalid action'}), 400