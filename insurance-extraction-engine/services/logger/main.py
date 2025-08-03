import os
import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from loguru import logger

app = FastAPI(title="Logger Service", version="1.0.0")

# Configure logging
os.makedirs("/app/logs", exist_ok=True)
logger.add("/app/logs/audit.log", rotation="10 MB", format="{time} | {level} | {message}")


class LogEntry(BaseModel):
    timestamp: Optional[datetime] = None
    level: str
    service: str
    message: str
    metadata: Optional[Dict[str, Any]] = None


class LogQuery(BaseModel):
    service: Optional[str] = None
    level: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    limit: Optional[int] = 100


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "service": "logger",
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": time.time()
    }


@app.post("/log")
async def log_entry(entry: LogEntry):
    """Log an entry"""
    try:
        if entry.timestamp is None:
            entry.timestamp = datetime.now()
        
        # Format log message
        log_message = f"{entry.service} | {entry.message}"
        if entry.metadata:
            log_message += f" | {json.dumps(entry.metadata)}"
        
        # Log based on level
        if entry.level.upper() == "ERROR":
            logger.error(log_message)
        elif entry.level.upper() == "WARNING":
            logger.warning(log_message)
        elif entry.level.upper() == "INFO":
            logger.info(log_message)
        elif entry.level.upper() == "DEBUG":
            logger.debug(log_message)
        else:
            logger.info(log_message)
        
        # Store in structured format for retrieval
        log_file = f"/app/logs/structured_{entry.service}.jsonl"
        with open(log_file, 'a') as f:
            f.write(json.dumps({
                "timestamp": entry.timestamp.isoformat(),
                "level": entry.level,
                "service": entry.service,
                "message": entry.message,
                "metadata": entry.metadata
            }) + "\n")
        
        return {
            "status": "logged",
            "timestamp": entry.timestamp,
            "service": entry.service
        }
        
    except Exception as e:
        logger.error(f"Error logging entry: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Logging failed: {str(e)}")


@app.post("/query")
async def query_logs(query: LogQuery):
    """Query logs based on criteria"""
    try:
        logs = []
        
        # If service specified, read from service-specific log
        if query.service:
            log_files = [f"/app/logs/structured_{query.service}.jsonl"]
        else:
            # Read from all structured log files
            log_files = []
            for filename in os.listdir("/app/logs"):
                if filename.startswith("structured_") and filename.endswith(".jsonl"):
                    log_files.append(f"/app/logs/{filename}")
        
        for log_file in log_files:
            if not os.path.exists(log_file):
                continue
                
            with open(log_file, 'r') as f:
                for line in f:
                    try:
                        log_entry = json.loads(line.strip())
                        
                        # Apply filters
                        if query.level and log_entry["level"].upper() != query.level.upper():
                            continue
                        
                        entry_time = datetime.fromisoformat(log_entry["timestamp"])
                        if query.start_time and entry_time < query.start_time:
                            continue
                        if query.end_time and entry_time > query.end_time:
                            continue
                        
                        logs.append(log_entry)
                        
                    except json.JSONDecodeError:
                        continue
        
        # Sort by timestamp (newest first)
        logs.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Apply limit
        if query.limit:
            logs = logs[:query.limit]
        
        return {
            "logs": logs,
            "total_count": len(logs),
            "query": query.dict()
        }
        
    except Exception as e:
        logger.error(f"Error querying logs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@app.get("/services")
async def list_services():
    """List all services that have logged entries"""
    try:
        services = []
        
        for filename in os.listdir("/app/logs"):
            if filename.startswith("structured_") and filename.endswith(".jsonl"):
                service_name = filename.replace("structured_", "").replace(".jsonl", "")
                
                # Get file stats
                file_path = f"/app/logs/{filename}"
                stat = os.stat(file_path)
                
                # Count lines (approximate entry count)
                with open(file_path, 'r') as f:
                    entry_count = sum(1 for _ in f)
                
                services.append({
                    "service": service_name,
                    "entry_count": entry_count,
                    "last_modified": datetime.fromtimestamp(stat.st_mtime),
                    "file_size": stat.st_size
                })
        
        return {"services": services}
        
    except Exception as e:
        logger.error(f"Error listing services: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Service listing failed: {str(e)}")


@app.get("/metrics/{service}")
async def get_service_metrics(service: str):
    """Get metrics for a specific service"""
    try:
        log_file = f"/app/logs/structured_{service}.jsonl"
        
        if not os.path.exists(log_file):
            raise HTTPException(status_code=404, detail="Service logs not found")
        
        metrics = {
            "service": service,
            "total_entries": 0,
            "level_counts": {"ERROR": 0, "WARNING": 0, "INFO": 0, "DEBUG": 0},
            "recent_entries": [],
            "error_rate": 0.0
        }
        
        recent_entries = []
        
        with open(log_file, 'r') as f:
            for line in f:
                try:
                    log_entry = json.loads(line.strip())
                    metrics["total_entries"] += 1
                    
                    level = log_entry["level"].upper()
                    if level in metrics["level_counts"]:
                        metrics["level_counts"][level] += 1
                    
                    recent_entries.append(log_entry)
                    
                except json.JSONDecodeError:
                    continue
        
        # Calculate error rate
        total_entries = metrics["total_entries"]
        if total_entries > 0:
            error_count = metrics["level_counts"]["ERROR"] + metrics["level_counts"]["WARNING"]
            metrics["error_rate"] = error_count / total_entries
        
        # Get recent entries (last 10)
        recent_entries.sort(key=lambda x: x["timestamp"], reverse=True)
        metrics["recent_entries"] = recent_entries[:10]
        
        return metrics
        
    except Exception as e:
        logger.error(f"Error getting metrics for service {service}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Metrics retrieval failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)