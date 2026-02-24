from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import base64, io
from PIL import Image
import numpy as np

# YOLO (Ultralytics)
from ultralytics import YOLO

app = FastAPI()

# You can swap to a better weapon model later.
# For hackathon: use yolov8n.pt and treat "knife" etc if available in your model,
# or use a custom trained weapon model if you have one.
model = YOLO("yolov8n.pt")

class ImageRequest(BaseModel):
    imageDataUrl: str

class TextRequest(BaseModel):
    text: str

def decode_data_url(data_url: str) -> Image.Image:
    if "," not in data_url:
        raise HTTPException(status_code=400, detail="Invalid imageDataUrl")
    header, b64 = data_url.split(",", 1)
    img_bytes = base64.b64decode(b64)
    return Image.open(io.BytesIO(img_bytes)).convert("RGB")

@app.post("/detect/weapon")
def detect_weapon(req: ImageRequest):
    img = decode_data_url(req.imageDataUrl)
    results = model.predict(source=np.array(img), verbose=False)[0]

    # NOTE: yolov8n COCO doesn't have "gun" class.
    # So this is a placeholder scoring strategy.
    # If you use a weapon-trained model, update class mapping.
    # We'll flag "person" count + confidence as weak proxy (demo).
    detected = False
    score = 0.0

    if results.boxes is not None and len(results.boxes) > 0:
        confs = results.boxes.conf.cpu().numpy().tolist()
        score = float(max(confs)) * 100.0

    # demo threshold
    if score > 65:
        detected = True

    return {
        "detected": detected,
        "score": round(score, 2),
        "riskDelta": 30 if detected else 5,
        "message": "⚠ Weapon-like threat detected (demo scoring)"
    }

@app.post("/detect/violence")
def detect_violence(req: ImageRequest):
    img = decode_data_url(req.imageDataUrl)

    # REAL violence detection usually needs video model (I3D/SlowFast) or pose/action model.
    # For now: placeholder using brightness/edge density heuristic.
    arr = np.array(img)
    edges_proxy = float(np.mean(np.abs(np.diff(arr.astype(np.float32), axis=0))))  # crude
    score = min(100.0, edges_proxy / 2.0)

    detected = score > 70
    return {
        "detected": detected,
        "score": round(score, 2),
        "riskDelta": 25 if detected else 4,
        "message": "⚠ Possible violent activity detected (heuristic demo)"
    }

@app.post("/text/analyze")
def text_analyze(req: TextRequest):
    text = (req.text or "").lower()
    keywords = ["coke", "heroin", "weed", "white powder", "crystal", "lsd", "buy now", "mdma", "meth"]
    hits = [k for k in keywords if k in text]
    score = min(100, len(hits) * 15)

    return {
        "hits": hits,
        "score": score,
        "riskDelta": min(40, score),
        "summary": f"Detected {len(hits)} suspicious keywords: {', '.join(hits) if hits else 'none'}"
    }