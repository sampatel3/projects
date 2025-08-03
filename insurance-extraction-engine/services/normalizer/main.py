import os
import re
import time
from typing import List, Dict, Any, Union
from datetime import datetime
from dateutil import parser as date_parser
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from loguru import logger

app = FastAPI(title="Normalizer Service", version="1.0.0")

# Configure logging
logger.add("logs/normalizer.log", rotation="10 MB")
os.makedirs("logs", exist_ok=True)


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


class CurrencyAmount(BaseModel):
    value: float
    currency: str


class ExtractedField(BaseModel):
    field_name: str
    value: Union[str, float, int, CurrencyAmount, datetime]
    confidence: float
    confidence_level: str
    source_tokens: List[OCRToken]
    extraction_method: str


class NormalizationRequest(BaseModel):
    job_id: str
    extracted_fields: List[ExtractedField]
    filename: str


class NormalizationResult(BaseModel):
    job_id: str
    normalized_fields: List[ExtractedField]
    insurance_submission: Dict[str, Any]
    confidence_metrics: Dict[str, Any]
    processing_time: float
    status: str


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "service": "normalizer",
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": time.time()
    }


def normalize_date(date_str: str) -> str:
    """Normalize date to ISO 8601 format"""
    try:
        # Try to parse various date formats
        parsed_date = date_parser.parse(date_str, fuzzy=True)
        return parsed_date.strftime("%Y-%m-%d")
    except:
        # If parsing fails, return original string
        return date_str


def normalize_currency(value_str: str) -> Union[CurrencyAmount, str]:
    """Normalize currency amounts"""
    try:
        # Extract currency code and amount
        currency_pattern = r'([A-Z]{3})'
        amount_pattern = r'([0-9,]+(?:\.[0-9]{2})?)'
        
        currency_match = re.search(currency_pattern, value_str)
        amount_match = re.search(amount_pattern, value_str)
        
        if currency_match and amount_match:
            currency = currency_match.group(1)
            amount_str = amount_match.group(1).replace(',', '')
            amount = float(amount_str)
            
            return CurrencyAmount(value=amount, currency=currency)
        else:
            return value_str
    except:
        return value_str


def normalize_text(text: str) -> str:
    """Normalize text fields"""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Capitalize properly
    if len(text) > 0 and text.isupper():
        # If all caps, convert to title case
        text = text.title()
    
    return text


def calculate_confidence_level(confidence: float) -> str:
    """Calculate confidence level category"""
    if confidence >= 0.90:
        return "high"
    elif confidence >= 0.75:
        return "medium"
    else:
        return "low"


def normalize_field(field: ExtractedField) -> ExtractedField:
    """Normalize a single field"""
    
    # Create a copy of the field
    normalized_field = field.copy()
    
    # Normalize based on field name
    if "date" in field.field_name.lower() or "period" in field.field_name.lower():
        if isinstance(field.value, str):
            normalized_field.value = normalize_date(field.value)
    
    elif "amount" in field.field_name.lower() or "currency" in field.field_name.lower():
        if isinstance(field.value, str):
            normalized_field.value = normalize_currency(field.value)
    
    elif isinstance(field.value, str):
        normalized_field.value = normalize_text(field.value)
    
    # Update confidence level
    normalized_field.confidence_level = calculate_confidence_level(field.confidence)
    
    return normalized_field


def create_insurance_submission(fields: List[ExtractedField]) -> Dict[str, Any]:
    """Create standardized insurance submission output"""
    
    # Initialize with None values
    submission = {
        "unique_market_reference": None,
        "type_of_insurance": None,
        "named_insured": None,
        "policy_period_start": None,
        "policy_period_end": None,
        "amount_of_insurance": None,
        "confidence_metrics": {}
    }
    
    # Map fields to submission
    field_mapping = {
        "unique_market_reference": "unique_market_reference",
        "umr": "unique_market_reference",
        "type_of_insurance": "type_of_insurance",
        "insurance_type": "type_of_insurance",
        "named_insured": "named_insured",
        "insured": "named_insured",
        "policy_period_start": "policy_period_start",
        "start_date": "policy_period_start",
        "effective_date": "policy_period_start",
        "policy_period_end": "policy_period_end",
        "end_date": "policy_period_end",
        "expiry_date": "policy_period_end",
        "amount_of_insurance": "amount_of_insurance",
        "sum_insured": "amount_of_insurance",
        "coverage_amount": "amount_of_insurance",
        "launch_date": "launch_date"  # For satellite insurance
    }
    
    confidence_metrics = {}
    
    for field in fields:
        # Find the correct mapping
        mapped_field = None
        for key, value in field_mapping.items():
            if key in field.field_name.lower():
                mapped_field = value
                break
        
        if mapped_field and mapped_field in submission:
            submission[mapped_field] = field.value
            confidence_metrics[mapped_field] = field.confidence
        elif field.field_name not in submission:
            # Add unmapped fields as well
            submission[field.field_name] = field.value
            confidence_metrics[field.field_name] = field.confidence
    
    # Calculate overall confidence metrics
    if confidence_metrics:
        avg_confidence = sum(confidence_metrics.values()) / len(confidence_metrics)
        submission["confidence_metrics"] = {
            "average_confidence": avg_confidence,
            "fields": confidence_metrics
        }
    
    return submission


@app.post("/normalize", response_model=NormalizationResult)
async def normalize_results(request: NormalizationRequest):
    """
    Normalize and validate extraction results
    """
    start_time = time.time()
    
    try:
        logger.info(f"Starting normalization for job {request.job_id}")
        
        # Normalize each field
        normalized_fields = []
        for field in request.extracted_fields:
            try:
                normalized_field = normalize_field(field)
                normalized_fields.append(normalized_field)
            except Exception as e:
                logger.warning(f"Error normalizing field {field.field_name}: {str(e)}")
                # Keep original field if normalization fails
                normalized_fields.append(field)
        
        # Create standardized insurance submission
        insurance_submission = create_insurance_submission(normalized_fields)
        
        # Extract confidence metrics
        confidence_metrics = insurance_submission.get("confidence_metrics", {})
        
        processing_time = time.time() - start_time
        
        result = NormalizationResult(
            job_id=request.job_id,
            normalized_fields=normalized_fields,
            insurance_submission=insurance_submission,
            confidence_metrics=confidence_metrics,
            processing_time=processing_time,
            status="completed"
        )
        
        logger.info(f"Normalization completed for job {request.job_id}: "
                   f"processed {len(normalized_fields)} fields in {processing_time:.2f}s")
        
        return result
        
    except Exception as e:
        logger.error(f"Error during normalization for job {request.job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Normalization failed: {str(e)}")


@app.post("/validate")
async def validate_submission(submission: Dict[str, Any]):
    """Validate insurance submission data"""
    try:
        validation_results = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "completeness_score": 0.0
        }
        
        # Required fields for insurance submission
        required_fields = [
            "unique_market_reference",
            "type_of_insurance", 
            "named_insured"
        ]
        
        # Check required fields
        missing_fields = []
        present_fields = 0
        
        for field in required_fields:
            if field not in submission or submission[field] is None:
                missing_fields.append(field)
                validation_results["errors"].append(f"Missing required field: {field}")
            else:
                present_fields += 1
        
        # Calculate completeness score
        total_possible_fields = len([k for k in submission.keys() if k != "confidence_metrics"])
        validation_results["completeness_score"] = present_fields / len(required_fields)
        
        # Check data quality
        if "confidence_metrics" in submission:
            avg_confidence = submission["confidence_metrics"].get("average_confidence", 0)
            if avg_confidence < 0.75:
                validation_results["warnings"].append(f"Low average confidence: {avg_confidence:.3f}")
        
        # Check date formats
        date_fields = ["policy_period_start", "policy_period_end", "launch_date"]
        for field in date_fields:
            if field in submission and submission[field]:
                try:
                    date_parser.parse(str(submission[field]))
                except:
                    validation_results["errors"].append(f"Invalid date format in {field}: {submission[field]}")
        
        # Check currency amounts
        if "amount_of_insurance" in submission and submission["amount_of_insurance"]:
            amount = submission["amount_of_insurance"]
            if isinstance(amount, dict):
                if "value" not in amount or "currency" not in amount:
                    validation_results["errors"].append("Invalid currency amount format")
                elif amount["value"] <= 0:
                    validation_results["errors"].append("Insurance amount must be positive")
        
        # Set overall validity
        validation_results["is_valid"] = len(validation_results["errors"]) == 0
        
        return validation_results
        
    except Exception as e:
        logger.error(f"Error during validation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)