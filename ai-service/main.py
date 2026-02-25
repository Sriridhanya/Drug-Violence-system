from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
import base64
import io
import re
from PIL import Image
import numpy as np

from ultralytics import YOLO

app = FastAPI(title="AI Drug Violence Detection - AI Service")

# Load your trained weapon model (must exist in ai-service/ as best.pt)
model = YOLO("best.pt")


class ImageRequest(BaseModel):
    imageDataUrl: str  # e.g. "data:image/jpeg;base64,...."


class TextRequest(BaseModel):
    text: str


@app.get("/")
def root():
    return {"status": "ai-service running"}


def decode_data_url(data_url: str) -> Image.Image:
    """Decode a browser Data URL (base64) into a PIL Image."""
    if not data_url or "," not in data_url:
        raise HTTPException(status_code=400, detail="Invalid imageDataUrl")

    header, b64 = data_url.split(",", 1)
    if "base64" not in header.lower():
        raise HTTPException(status_code=400, detail="Invalid imageDataUrl (missing base64 header)")

    try:
        img_bytes = base64.b64decode(b64)
        return Image.open(io.BytesIO(img_bytes)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid imageDataUrl (cannot decode image)")


@app.post("/detect/weapon")
def detect_weapon(req: ImageRequest):
    """Weapon detection from React base64 imageDataUrl."""
    img = decode_data_url(req.imageDataUrl)
    results = model.predict(source=np.array(img), conf=0.25, verbose=False)[0]

    detected = False
    max_score = 0.0
    classes = []

    if results.boxes is not None and len(results.boxes) > 0:
        for box in results.boxes:
            confv = float(box.conf.cpu().numpy())
            cls_id = int(box.cls.cpu().numpy())
            name = model.names.get(cls_id, str(cls_id))  # safe mapping
            classes.append(name)
            detected = True
            max_score = max(max_score, confv * 100)

    return {
        "detected": detected,
        "score": round(max_score, 2),
        "classes": classes,
        "riskDelta": 40 if detected else 5,
        "message": "⚠ Weapon detected!" if detected else "No weapon detected",
    }


@app.post("/detect/weapon_file")
async def detect_weapon_file(file: UploadFile = File(...)):
    """Weapon detection by uploading an image file (easy Swagger testing)."""
    try:
        img_bytes = await file.read()
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file")

    results = model.predict(source=np.array(img), conf=0.25, verbose=False)[0]

    detected = False
    max_score = 0.0
    classes = []

    if results.boxes is not None and len(results.boxes) > 0:
        for box in results.boxes:
            confv = float(box.conf.cpu().numpy())
            cls_id = int(box.cls.cpu().numpy())
            name = model.names.get(cls_id, str(cls_id))
            classes.append(name)
            detected = True
            max_score = max(max_score, confv * 100)

    return {
        "detected": detected,
        "score": round(max_score, 2),
        "classes": classes,
        "riskDelta": 40 if detected else 5,
        "message": "⚠ Weapon detected!" if detected else "No weapon detected",
    }


@app.post("/detect/violence")
def detect_violence(req: ImageRequest):
    """
    Placeholder violence scoring.
    Real violence detection typically needs video/action recognition models.
    """
    img = decode_data_url(req.imageDataUrl)
    arr = np.array(img).astype(np.float32)

    edges_proxy = float(np.mean(np.abs(np.diff(arr, axis=0))))
    score = min(100.0, edges_proxy / 2.0)
    detected = score > 70.0

    return {
        "detected": detected,
        "score": round(score, 2),
        "riskDelta": 25 if detected else 4,
        "message": "⚠ Possible violent activity detected (heuristic)" if detected else "Normal activity",
    }


# ---------------------------
# Improved Text/NLP Detection
# ---------------------------
DRUG_TERMS = {
    "hard_drugs": (["heroin", "cocaine", "coke", "meth", "ice", "mdma", "ecstasy", "lsd", "acid"], 25),
    "cannabis": (["weed", "ganja", "marijuana", "hash", "charas", "joint"], 12),
    "buy_sell": (["buy", "sell", "price", "rate", "available", "delivery", "ship", "deal", "bulk"], 18),
    "stealth": (["dm", "pm", "telegram", "snap", "signal", "wickr", "crypto", "btc", "monero"], 15),
    "units": (["gram", "g", "gms", "oz", "ounce", "kg", "kilo", "tabs", "pills"], 10),
}


def normalize_text(s: str) -> str:
    s = (s or "").lower()
    s = re.sub(r"\s+", " ", s).strip()
    return s


@app.post("/text/analyze")
def text_analyze(req: TextRequest):
    text = normalize_text(req.text)

    hits = []
    score = 0

    for _, (terms, weight) in DRUG_TERMS.items():
        group_hits = [t for t in terms if t in text]
        if group_hits:
            hits.extend(group_hits)
            score += weight

    hits_unique = sorted(set(hits))
    score = min(100, score)

    return {
        "hits": hits_unique,
        "score": score,
        "riskDelta": min(40, score),
        "summary": f"Found {len(hits_unique)} suspicious terms.",
    }