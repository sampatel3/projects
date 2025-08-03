import os
import time
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from paddleocr import PaddleOCR
import cv2
import numpy as np
from PIL import Image
from loguru import logger

app = FastAPI(title="PaddleOCR Service", version="1.0.0")

# Configure logging
logger.add("logs/paddleocr.log", rotation="10 MB")
os.makedirs("logs", exist_ok=True)

# Initialize PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)


class BoundingBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float


class OCRToken(BaseModel):
    text: str
    bbox: BoundingBox
    confidence: float
    page: int


class OCRRequest(BaseModel):
    job_id: str
    image_paths: List[Dict[str, Any]]


class OCRResult(BaseModel):
    job_id: str
    tokens: List[OCRToken]
    page_count: int
    processing_time: float
    status: str


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "service": "paddleocr",
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": time.time()
    }


def normalize_bbox(bbox_points, img_width, img_height):
    """
    Convert PaddleOCR bbox format to normalized coordinates
    PaddleOCR returns 4 corner points, we convert to x1,y1,x2,y2
    """
    # Extract all x and y coordinates
    x_coords = [point[0] for point in bbox_points]
    y_coords = [point[1] for point in bbox_points]
    
    # Get bounding box
    x1, x2 = min(x_coords), max(x_coords)
    y1, y2 = min(y_coords), max(y_coords)
    
    return BoundingBox(
        x1=x1 / img_width,
        y1=y1 / img_height,
        x2=x2 / img_width,
        y2=y2 / img_height
    )


@app.post("/extract", response_model=OCRResult)
async def extract_text(request: OCRRequest):
    """
    Extract text from images using PaddleOCR
    Returns structured OCR tokens with bounding boxes and confidence scores
    """
    start_time = time.time()
    
    try:
        logger.info(f"Starting OCR extraction for job {request.job_id}")
        
        all_tokens = []
        
        for page_info in request.image_paths:
            page_num = page_info["page"]
            image_path = page_info["path"]
            
            if not os.path.exists(image_path):
                logger.error(f"Image not found: {image_path}")
                continue
            
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"Failed to load image: {image_path}")
                continue
                
            img_height, img_width = image.shape[:2]
            
            # Run OCR
            result = ocr.ocr(image, cls=True)
            
            # Process OCR results
            if result and result[0]:
                for line in result[0]:
                    bbox_points = line[0]  # 4 corner points
                    text_info = line[1]    # (text, confidence)
                    
                    text = text_info[0]
                    confidence = text_info[1]
                    
                    # Skip empty or very low confidence results
                    if not text.strip() or confidence < 0.1:
                        continue
                    
                    # Normalize bounding box
                    normalized_bbox = normalize_bbox(bbox_points, img_width, img_height)
                    
                    token = OCRToken(
                        text=text.strip(),
                        bbox=normalized_bbox,
                        confidence=confidence,
                        page=page_num
                    )
                    
                    all_tokens.append(token)
        
        processing_time = time.time() - start_time
        
        result = OCRResult(
            job_id=request.job_id,
            tokens=all_tokens,
            page_count=len(request.image_paths),
            processing_time=processing_time,
            status="completed"
        )
        
        logger.info(f"OCR extraction completed for job {request.job_id}: "
                   f"{len(all_tokens)} tokens in {processing_time:.2f}s")
        
        return result
        
    except Exception as e:
        logger.error(f"Error during OCR extraction for job {request.job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"OCR extraction failed: {str(e)}")


@app.post("/extract_single")
async def extract_single_image(image_path: str):
    """
    Extract text from a single image
    Utility endpoint for testing
    """
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")
    
    try:
        # Load image
        image = cv2.imread(image_path)
        img_height, img_width = image.shape[:2]
        
        # Run OCR
        result = ocr.ocr(image, cls=True)
        
        tokens = []
        if result and result[0]:
            for line in result[0]:
                bbox_points = line[0]
                text_info = line[1]
                
                text = text_info[0]
                confidence = text_info[1]
                
                if not text.strip() or confidence < 0.1:
                    continue
                
                normalized_bbox = normalize_bbox(bbox_points, img_width, img_height)
                
                token = OCRToken(
                    text=text.strip(),
                    bbox=normalized_bbox,
                    confidence=confidence,
                    page=0
                )
                
                tokens.append(token)
        
        return {
            "tokens": tokens,
            "total_tokens": len(tokens),
            "image_path": image_path
        }
        
    except Exception as e:
        logger.error(f"Error processing single image {image_path}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)