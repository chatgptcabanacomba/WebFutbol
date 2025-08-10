from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
import yt_dlp

# Directorio donde se guardan los vídeos
video_dir = "videos"
os.makedirs("videos", exist_ok=True)

app = FastAPI()

# Montar la carpeta de vídeos como ruta estática
from fastapi.staticfiles import StaticFiles
import os
app.mount("/videos", StaticFiles(directory=os.path.join(os.path.dirname(__file__), video_dir)), name="videos")


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Variable global para progreso
progreso_actual = {"porcentaje": 0.0}

@app.post("/descargar")
async def descargar_video(url: str = Form(...)):
    global progreso_actual
    progreso_actual["porcentaje"] = 0.0

    nombre_archivo = f"{uuid.uuid4()}.mp4"
    ruta_salida = os.path.join(video_dir, nombre_archivo)

    def hook(d):
        if d["status"] == "downloading":
            progreso_actual["porcentaje"] = d.get("progress", {}).get("_percent", 0.0)

    ydl_opts = {
    "format": "best[ext=mp4]/best",
    "merge_output_format": "mp4",
    "outtmpl": ruta_salida,
    "progress_hooks": [hook]
}


    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return {"ruta": f"/videos/{nombre_archivo}"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/progreso")
async def obtener_progreso():
    global progreso_actual
    return {"porcentaje": round(progreso_actual["porcentaje"] * 100, 1)}
