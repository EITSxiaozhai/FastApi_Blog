import asyncio
import datetime
import time
from fastapi import APIRouter
from fastapi import FastAPI, WebSocket
import psutil  # 用于获取系统信息
from starlette.responses import HTMLResponse

MonitoringApp = APIRouter()


# WebSocket 路由
@MonitoringApp.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    while True:
        memory_info = psutil.virtual_memory()
        memory_percent = (memory_info.used / memory_info.total) * 100
        current_time = datetime.datetime.now().isoformat()
        print(current_time)
        await websocket.send_json(f"{current_time},{memory_percent:.0f}")  # 发送保留两位小数的百分比数字
        await asyncio.sleep(1)