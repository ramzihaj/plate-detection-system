from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from videotest import VideoProcessor

app = FastAPI()
app.mount("/templates", StaticFiles(directory="templates"), name="templates")

video_path = "static/video/test3.mp4"  # ou 0 pour webcam
processor = VideoProcessor(video_path)
processor.start()

@app.get("/")
async def get():
    return FileResponse("templates/indexForVideo.html")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            result = processor.get_latest_result()
            if result:
                await websocket.send_json(result)
    except Exception as e:
        print(f"WebSocket Error: {e}")
    finally:
        await websocket.close()
