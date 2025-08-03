import os
import sys
import io
from pathlib import Path
from typing import List, Dict, Any, Optional
import traceback
import random

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from PIL import Image
import numpy as np
from loguru import logger

# Add parent directory to path for shared imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from shared.models import OCRResult, OCRToken, BoundingBox, ServiceHealth

app = FastAPI(title="PaddleOCR Service (Mock)", version="1.0.0")

@app.get("/health", response_model=ServiceHealth)
async def health_check():
    """Health check endpoint"""
    return ServiceHealth(
        service="paddleocr",
        status="healthy",
        message="Mock PaddleOCR service is running (simulates OCR without model downloads)"
    )

@app.post("/extract", response_model=OCRResult)
async def extract_text(file: UploadFile = File(...)):
    """Extract text from image using Mock PaddleOCR (for demonstration purposes)"""
    try:
        logger.info(f"Processing OCR request for file: {file.filename}")
        
        # Read and process image
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        
        logger.info("Running mock OCR extraction...")
        
        # Mock OCR results - simulate typical insurance document fields
        mock_tokens = [
            {
                "text": "INSURANCE POLICY",
                "bbox": {"x": 100, "y": 50, "width": 200, "height": 25},
                "confidence": 0.95
            },
            {
                "text": "Policy Number: INS-2024-001234",
                "bbox": {"x": 50, "y": 100, "width": 300, "height": 20},
                "confidence": 0.92
            },
            {
                "text": "Insured Name: John Smith",
                "bbox": {"x": 50, "y": 130, "width": 250, "height": 20},
                "confidence": 0.89
            },
            {
                "text": "Premium Amount: $1,250.00",
                "bbox": {"x": 50, "y": 160, "width": 200, "height": 20},
                "confidence": 0.94
            },
            {
                "text": "Effective Date: 01/01/2024",
                "bbox": {"x": 50, "y": 190, "width": 180, "height": 20},
                "confidence": 0.91
            },
            {
                "text": "Coverage Type: Comprehensive",
                "bbox": {"x": 50, "y": 220, "width": 220, "height": 20},
                "confidence": 0.88
            }
        ]
        
        # Convert mock data to proper format
        tokens = []
        for mock_token in mock_tokens:
            bbox = BoundingBox(
                x=mock_token["bbox"]["x"],
                y=mock_token["bbox"]["y"],
                width=mock_token["bbox"]["width"],
                height=mock_token["bbox"]["height"]
            )
            
            token = OCRToken(
                text=mock_token["text"],
                confidence=mock_token["confidence"],
                bbox=bbox
            )
            tokens.append(token)
        
        logger.info(f"Mock OCR extraction completed. Generated {len(tokens)} text tokens")
        
        return OCRResult(
            tokens=tokens,
            image_width=image.width,
            image_height=image.height,
            processing_time=0.5  # Mock processing time
        )
        
    except Exception as e:
        logger.error(f"Mock OCR extraction failed: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"OCR extraction failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)