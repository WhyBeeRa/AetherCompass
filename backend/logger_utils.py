import asyncio
from typing import Set
from fastapi import WebSocket
from datetime import datetime

class LogStreamer:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LogStreamer, cls).__new__(cls)
            cls._instance.connections: Set[WebSocket] = set()
        return cls._instance

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.add(websocket)
        # Send initial message
        await websocket.send_text(f"[{datetime.now().strftime('%H:%M:%S')}] [SYSTEM] Terminal Link Established.")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.connections:
            self.connections.remove(websocket)

    async def broadcast(self, message: str):
        if not self.connections:
            return
            
        disconnected = set()
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        
        for connection in self.connections:
            try:
                await connection.send_text(formatted_message)
            except Exception:
                disconnected.add(connection)
        
        for conn in disconnected:
            self.connections.remove(conn)

log_streamer = LogStreamer()

async def log_terminal(message: str):
    # Also write to background_tasks.log for persistence
    try:
        with open("background_tasks.log", "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now()}] {message}\n")
    except Exception:
        pass
        
    await log_streamer.broadcast(message)
