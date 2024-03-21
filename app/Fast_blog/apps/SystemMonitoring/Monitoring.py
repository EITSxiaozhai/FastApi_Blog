import asyncio
import datetime
import time
from typing import List

from fastapi import APIRouter
from fastapi import WebSocket
import psutil  # 用于获取系统信息

MonitoringApp = APIRouter()


# WebSocket 路由
class ConnectionManager:
    def __init__(self):
        # 存放激活的ws连接对象
        self.active_connections: List[WebSocket] = []

    async def connect(self, ws: WebSocket):
        # 等待连接
        await ws.accept()
        # 存储ws连接对象
        self.active_connections.append(ws)

    def disconnect(self, ws: WebSocket):
        # 关闭时 移除ws对象
        self.active_connections.remove(ws)


manager = ConnectionManager()


@MonitoringApp.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        while True:
            memory_info = psutil.virtual_memory()
            memory_percent = (memory_info.used / memory_info.total) * 100
            cpu_info = psutil.cpu_percent()
            current_time = datetime.datetime.now().isoformat()
            await websocket.send_json(
                {"cpu_info": cpu_info, "memory_percent": memory_percent,
                 "current_time": current_time})  # 发送保留两位小数的百分比数字
            await asyncio.sleep(1)
    except Exception as e:
        # 捕获异常，表示连接断开
        print(f"WebSocket Connection Closed: {str(e)}")
    finally:
        manager.disconnect(websocket)
