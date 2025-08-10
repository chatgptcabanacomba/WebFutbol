from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os, uuid, yt_dlp

video_dir = "videos"
os.makedirs(video_dir, exist_ok=True)

app = FastAPI()

# Static files
from fastapi.staticfiles import StaticFiles
app.mount("/videos", StaticFiles(directory=os.path.join(os.path.dirname(__file__), video_dir)), name="videos")
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global progress
progreso_actual = {"porcentaje": 0.0}

@app.post("/descargar")
async def descargar_video(url: str = Form(...)):
    global progreso_actual
    progreso_actual["porcentaje"] = 0.0
    nombre_archivo = f"{uuid.uuid4()}.mp4"
    ruta_salida = os.path.join(video_dir, nombre_archivo)

    def hook(d):
        if d.get("status") == "downloading":
            progreso_actual["porcentaje"] = d.get("downloaded_bytes", 0) / max(d.get("total_bytes", 1), 1) * 100

    ydl_opts = {
        "format": "best[ext=mp4]/best",
        "merge_output_format": "mp4",
        "outtmpl": ruta_salida,
        "progress_hooks": [hook],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

    return {"video_url": f"/videos/{nombre_archivo}"}

@app.get("/progreso")
async def progreso():
    return progreso_actual

