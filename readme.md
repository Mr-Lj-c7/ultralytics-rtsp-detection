# ---- 基于yolo检测模型对多路摄像头视频流进行目标检测 ----

- 说明
'''
该项目基于ultralytics利用yolo检测模型对多路摄像头视频流进行目标检测，并同步到web端进行可视化，模型采用CPU单线程进行推理，平均时延在60ms左右；
利用Flask进行模块封装http协议传输到web端可视化结果，本项目主要为yolo的部署提供参考，实际工程化部署需要结合实际的业务场景进行优化。
'''

## 1. 运行环境
1. windows11 x64
2. CPU: intel i5-9400F
3. GPU: Radeon RX 550X
4. RAM: 16G
5. utralytics==8.3.119

## 2. 运行方法
1. 安装ultralytics（建议在conda环境中进行）
```
pip install ultralytics flask-socketio 
```
2. 运行代码
```
python main.py
```

## 3. 项目结构
### 3.1.  主模块 
'''
多摄像头rtsp视频流接入yolo模型进行检测，同步web端可视化
'''

- 目录结构:
'''
. rtsp/
| config/
    |   config.json
|   log/
    |   rtsp_20250523_165622.log
|   modle/
    |   yolov8n.pt
|   templates/
    |   multi_cam.html
|   src/
    |   main.py
    |   logger.py
    |   shared.py
    |   config_loader.py
    |   frames_reader.py
    |   frames_process.py
    |   web_show.py
'''


### 3.2. 测试模块
'''
测试单摄像头画面检测rtsp视频流，main.py
'''

- 目录结构:
'''
. rtsp/
|   test/
    |   config
        |   config.json
    |   log/
        |   rtsp.log
    |  static/ 
        |   style.css
    |   templates/
        |   index.html
    |   src/
        |   main.py
        |   logger.py
        |   shared.py
        |   config_loader.py
        |   frames_reader.py
        |   frames_process.py
        |   show.py
'''
## 4. 项目说明链接
https://blog.csdn.net/qq_57674776/article/details/148236729?spm=1011.2124.3001.6209
