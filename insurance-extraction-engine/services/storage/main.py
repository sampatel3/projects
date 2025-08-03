import os
import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from loguru import logger

app = FastAPI(title="Storage Service", version="1.0.0")

# Configure logging
logger.add("logs/storage.log", rotation="10 MB")
os.makedirs("logs", exist_ok=True)

# Create output directories
os.makedirs("/app/outputs/extracted_data", exist_ok=True)
os.makedirs("/app/outputs/confidence_metrics", exist_ok=True)


class StorageRequest(BaseModel):
    job_id: str
    filename: str
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None


class StorageResult(BaseModel):
    job_id: str
    stored_paths: List[str]
    status: str
    timestamp: datetime


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "service": "storage",
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": time.time()
    }


@app.post("/store", response_model=StorageResult)
async def store_results(request: StorageRequest):
    """
    Store extraction results to disk
    """
    try:
        logger.info(f"Storing results for job {request.job_id}")
        
        stored_paths = []
        timestamp = datetime.now()
        
        # Store main extraction data
        extraction_file = f"/app/outputs/extracted_data/{request.job_id}_extraction.json"
        with open(extraction_file, 'w') as f:
            json.dump(request.data, f, indent=2, default=str)
        stored_paths.append(extraction_file)
        
        # Store confidence metrics separately
        if "confidence_metrics" in request.data:
            metrics_file = f"/app/outputs/confidence_metrics/{request.job_id}_metrics.json"
            with open(metrics_file, 'w') as f:
                json.dump(request.data["confidence_metrics"], f, indent=2, default=str)
            stored_paths.append(metrics_file)
        
        # Store metadata if provided
        if request.metadata:
            metadata_file = f"/app/outputs/extracted_data/{request.job_id}_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(request.metadata, f, indent=2, default=str)
            stored_paths.append(metadata_file)
        
        result = StorageResult(
            job_id=request.job_id,
            stored_paths=stored_paths,
            status="completed",
            timestamp=timestamp
        )
        
        logger.info(f"Storage completed for job {request.job_id}: {len(stored_paths)} files stored")
        
        return result
        
    except Exception as e:
        logger.error(f"Error storing results for job {request.job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Storage failed: {str(e)}")


@app.get("/retrieve/{job_id}")
async def retrieve_results(job_id: str):
    """Retrieve stored results for a job"""
    try:
        extraction_file = f"/app/outputs/extracted_data/{job_id}_extraction.json"
        
        if not os.path.exists(extraction_file):
            raise HTTPException(status_code=404, detail="Results not found")
        
        with open(extraction_file, 'r') as f:
            data = json.load(f)
        
        # Try to load metadata if exists
        metadata_file = f"/app/outputs/extracted_data/{job_id}_metadata.json"
        metadata = None
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
        
        return {
            "job_id": job_id,
            "data": data,
            "metadata": metadata,
            "retrieved_at": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error retrieving results for job {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {str(e)}")


@app.get("/list")
async def list_stored_jobs():
    """List all stored jobs"""
    try:
        extraction_dir = "/app/outputs/extracted_data"
        
        if not os.path.exists(extraction_dir):
            return {"jobs": []}
        
        jobs = []
        for filename in os.listdir(extraction_dir):
            if filename.endswith("_extraction.json"):
                job_id = filename.replace("_extraction.json", "")
                file_path = os.path.join(extraction_dir, filename)
                stat = os.stat(file_path)
                
                jobs.append({
                    "job_id": job_id,
                    "stored_at": datetime.fromtimestamp(stat.st_mtime),
                    "file_size": stat.st_size
                })
        
        # Sort by stored time (newest first)
        jobs.sort(key=lambda x: x["stored_at"], reverse=True)
        
        return {"jobs": jobs}
        
    except Exception as e:
        logger.error(f"Error listing stored jobs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Listing failed: {str(e)}")


@app.delete("/delete/{job_id}")
async def delete_results(job_id: str):
    """Delete stored results for a job"""
    try:
        deleted_files = []
        
        # Delete extraction file
        extraction_file = f"/app/outputs/extracted_data/{job_id}_extraction.json"
        if os.path.exists(extraction_file):
            os.remove(extraction_file)
            deleted_files.append(extraction_file)
        
        # Delete metrics file
        metrics_file = f"/app/outputs/confidence_metrics/{job_id}_metrics.json"
        if os.path.exists(metrics_file):
            os.remove(metrics_file)
            deleted_files.append(metrics_file)
        
        # Delete metadata file
        metadata_file = f"/app/outputs/extracted_data/{job_id}_metadata.json"
        if os.path.exists(metadata_file):
            os.remove(metadata_file)
            deleted_files.append(metadata_file)
        
        if not deleted_files:
            raise HTTPException(status_code=404, detail="No files found to delete")
        
        logger.info(f"Deleted {len(deleted_files)} files for job {job_id}")
        
        return {
            "job_id": job_id,
            "deleted_files": deleted_files,
            "status": "completed"
        }
        
    except Exception as e:
        logger.error(f"Error deleting results for job {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)