import os
import uuid
from typing import List
from pathlib import Path
import fitz  # PyMuPDF
from pdf2image import convert_from_path
from PIL import Image
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from loguru import logger
import time

app = FastAPI(title="PDF Renderer Service", version="1.0.0")

# Configure logging
logger.add("logs/pdf_renderer.log", rotation="10 MB")

# Create necessary directories
os.makedirs("/app/outputs/rendered_pages", exist_ok=True)
os.makedirs("/app/data", exist_ok=True)
os.makedirs("logs", exist_ok=True)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "service": "pdf-renderer",
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": time.time()
    }


@app.post("/render")
async def render_pdf(file: UploadFile = File(...)):
    """
    Convert PDF to high-resolution images (300 DPI)
    Returns list of image paths and metadata
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    start_time = time.time()
    job_id = str(uuid.uuid4())
    
    try:
        # Save uploaded PDF
        pdf_path = f"/app/data/{job_id}_{file.filename}"
        with open(pdf_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        logger.info(f"Processing PDF: {file.filename} (Job ID: {job_id})")
        
        # Get page count using PyMuPDF
        pdf_doc = fitz.open(pdf_path)
        page_count = pdf_doc.page_count
        pdf_doc.close()
        
        # Convert PDF to images at 300 DPI
        images = convert_from_path(
            pdf_path, 
            dpi=300,
            output_folder=f"/app/outputs/rendered_pages/{job_id}",
            fmt='png'
        )
        
        # Save images and collect metadata
        image_paths = []
        for i, image in enumerate(images):
            image_filename = f"page_{i:03d}.png"
            image_path = f"/app/outputs/rendered_pages/{job_id}/{image_filename}"
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(image_path), exist_ok=True)
            
            # Save image
            image.save(image_path, "PNG", optimize=True)
            image_paths.append({
                "page": i,
                "path": image_path,
                "width": image.width,
                "height": image.height,
                "dpi": 300
            })
        
        processing_time = time.time() - start_time
        
        result = {
            "job_id": job_id,
            "filename": file.filename,
            "page_count": page_count,
            "images": image_paths,
            "processing_time": processing_time,
            "status": "completed"
        }
        
        logger.info(f"PDF rendering completed: {file.filename} - {page_count} pages in {processing_time:.2f}s")
        
        # Clean up original PDF
        os.remove(pdf_path)
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing PDF {file.filename}: {str(e)}")
        
        # Clean up on error
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
            
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


@app.get("/job/{job_id}")
async def get_job_result(job_id: str):
    """Get rendered images for a specific job"""
    job_dir = f"/app/outputs/rendered_pages/{job_id}"
    
    if not os.path.exists(job_dir):
        raise HTTPException(status_code=404, detail="Job not found")
    
    # List all PNG files in job directory
    image_files = sorted([f for f in os.listdir(job_dir) if f.endswith('.png')])
    
    images = []
    for i, filename in enumerate(image_files):
        image_path = os.path.join(job_dir, filename)
        
        # Get image dimensions
        with Image.open(image_path) as img:
            width, height = img.size
        
        images.append({
            "page": i,
            "path": image_path,
            "width": width,
            "height": height,
            "dpi": 300
        })
    
    return {
        "job_id": job_id,
        "page_count": len(images),
        "images": images,
        "status": "completed"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)