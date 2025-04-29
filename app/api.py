from fastapi import APIRouter, UploadFile, File
from fastapi.responses import StreamingResponse, JSONResponse, Response
import io
import cv2
import json
from app.utils import process_image
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/process-image")
async def process_image_endpoint(file: UploadFile = File(...)):
    """Returns only the processed image."""
    try:
        contents = await file.read()
        processed_image, detections = process_image(contents)

        _, encoded_img = cv2.imencode('.png', processed_image)
        img_bytes = encoded_img.tobytes()

        return StreamingResponse(io.BytesIO(img_bytes), media_type="image/png")
    except Exception as e:
        logger.error(f"Failed to process the image: {e}")
        return JSONResponse(status_code=500, content={"message": "Failed to process the image."})

@router.post("/process-json")
async def process_json_endpoint(file: UploadFile = File(...)):
    """Returns only the detection results in JSON."""
    try:
        contents = await file.read()
        _, detections = process_image(contents)

        return JSONResponse(content={"detections": detections})
    except Exception as e:
        logger.error(f"Failed to process the image: {e}")
        return JSONResponse(status_code=500, content={"message": "Failed to process the image."})


