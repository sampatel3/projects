import os
import sys
import io
from pathlib import Path
from typing import List, Dict, Any, Optional
import traceback

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from PIL import Image
import numpy as np
from loguru import logger

# Add parent directory to path for shared imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from shared.models import OCRResult, OCRToken, BoundingBox, ServiceHealth

app = FastAPI(title="PaddleOCR Service", version="1.0.0")

# Global OCR instance - will be initialized lazily
ocr_instance = None

def get_ocr_instance():
    """Lazy initialization of PaddleOCR instance"""
    global ocr_instance
    if ocr_instance is None:
        try:
            from paddleocr import PaddleOCR
            logger.info("Initializing PaddleOCR...")
            ocr_instance = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
            logger.info("PaddleOCR initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize PaddleOCR: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(
                status_code=503, 
                detail=f"OCR service unavailable: {str(e)}"
            )
    return ocr_instance

@app.get("/health", response_model=ServiceHealth)
async def health_check():
    """Health check endpoint"""
    try:
        # Don't initialize OCR during health check to avoid startup issues
        return ServiceHealth(
            service="paddleocr",
            status="healthy",
            message="PaddleOCR service is running (OCR models will be loaded on first use)"
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return ServiceHealth(
            service="paddleocr",
            status="unhealthy",
            message=f"Service error: {str(e)}"
        )

@app.post("/extract", response_model=OCRResult)
async def extract_text(file: UploadFile = File(...)):
    """Extract text from image using PaddleOCR"""
    try:
        logger.info(f"Processing OCR request for file: {file.filename}")
        
        # Initialize OCR instance on first use
        ocr = get_ocr_instance()
        
        # Read and process image
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        
        # Convert PIL image to numpy array
        image_array = np.array(image)
        
        # Perform OCR
        logger.info("Running OCR extraction...")
        results = ocr.ocr(image_array, cls=True)
        
        # Process results
        tokens = []
        if results and results[0]:  # Check if results exist and are not empty
            for line in results[0]:
                if line and len(line) >= 2:  # Ensure line has bbox and text info
                    bbox_coords = line[0]  # [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                    text_info = line[1]    # (text, confidence)
                    
                    if bbox_coords and text_info and len(text_info) >= 2:
                        text = text_info[0]
                        confidence = float(text_info[1])
                        
                        # Convert bbox coordinates
                        # PaddleOCR returns 4 corner points, we'll use min/max for rectangle
                        x_coords = [point[0] for point in bbox_coords]
                        y_coords = [point[1] for point in bbox_coords]
                        
                        bbox = BoundingBox(
                            x=min(x_coords),
                            y=min(y_coords),
                            width=max(x_coords) - min(x_coords),
                            height=max(y_coords) - min(y_coords)
                        )
                        
                        token = OCRToken(
                            text=text,
                            confidence=confidence,
                            bbox=bbox
                        )
                        tokens.append(token)
        
        logger.info(f"OCR extraction completed. Found {len(tokens)} text tokens")
        
        return OCRResult(
            tokens=tokens,
            image_width=image.width,
            image_height=image.height,
            processing_time=0.0  # We'll calculate this later if needed
        )
        
    except Exception as e:
        logger.error(f"OCR extraction failed: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"OCR extraction failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)