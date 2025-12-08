# backend/app.py
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from transformers import pipeline
from PIL import Image
import io
import traceback
import threading
import numpy as np
import sys

app = FastAPI(title="Brain Tumor Detector (Hemgg ViT)")

# Allow local frontend (tighten in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- NUMPY VERSION CHECK ---
try:
    _np_version = tuple(map(int, np.__version__.split(".")[:2]))
except Exception:
    _np_version = (99, 0)
if _np_version[0] >= 2:
    _NUMPY_INCOMPATIBLE = True
    _NUMPY_MSG = (
        f"Incompatible NumPy version detected: {np.__version__}. "
        "Please install numpy<2 (e.g. `pip install \"numpy<2\"`) and restart the server."
    )
    print("WARNING:", _NUMPY_MSG, file=sys.stderr)
else:
    _NUMPY_INCOMPATIBLE = False
    _NUMPY_MSG = ""

# --- MODEL CONFIG ---
MODEL_ID = "Hemgg/brain-tumor-classification"

classifier = None
classifier_lock = threading.Lock()


def get_classifier():
    global classifier
    if classifier is None:
        with classifier_lock:
            if classifier is None:
                if _NUMPY_INCOMPATIBLE:
                    raise RuntimeError(_NUMPY_MSG)
                print(f"Loading model: {MODEL_ID} ...")
                classifier = pipeline("image-classification", model=MODEL_ID, use_fast=True)
                print("Model loaded successfully.")
    return classifier


@app.get("/")
async def root():
    if _NUMPY_INCOMPATIBLE:
        return JSONResponse({"error": "Incompatible NumPy version", "detail": _NUMPY_MSG}, status_code=500)
    return {"message": f"Brain Tumor Detector API running (model: {MODEL_ID})"}


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if _NUMPY_INCOMPATIBLE:
        return JSONResponse({"error": "Incompatible NumPy version", "detail": _NUMPY_MSG}, status_code=500)

    contents = await file.read()
    try:
        image = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception:
        tb = traceback.format_exc()
        print("IMAGE LOAD ERROR:\n", tb)
        return JSONResponse({"error": "Invalid image file", "traceback": tb}, status_code=400)

    try:
        clf = get_classifier()
    except Exception:
        tb = traceback.format_exc()
        print("CLASSIFIER INIT ERROR:\n", tb)
        return JSONResponse({"error": "Failed to initialize classifier", "traceback": tb}, status_code=500)

    try:
        # pass a batch of one to ensure proper preprocessing
        batch_results = clf([image], top_k=4)
        preds_for_image = batch_results[0]
        return {"predictions": preds_for_image}
    except Exception:
        tb = traceback.format_exc()
        print("INFERENCE ERROR:\n", tb)
        return JSONResponse({"error": "Model inference failed", "traceback": tb}, status_code=500)