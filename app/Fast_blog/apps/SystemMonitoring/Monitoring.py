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
        cpu_info = psutil.cpu_percent()
        current_time = datetime.datetime.now().isoformat()
        await websocket.send_json(
            {"cpu_info": cpu_info, "memory_percent": memory_percent, "current_time": current_time})  # 发送保留两位小数的百分比数字
        await asyncio.sleep(1)
