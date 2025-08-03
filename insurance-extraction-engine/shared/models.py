from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class ConfidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium" 
    LOW = "low"


class BoundingBox(BaseModel):
    x1: float = Field(..., description="Left coordinate")
    y1: float = Field(..., description="Top coordinate")
    x2: float = Field(..., description="Right coordinate")
    y2: float = Field(..., description="Bottom coordinate")
    

class OCRToken(BaseModel):
    text: str = Field(..., description="Recognized text")
    bbox: BoundingBox = Field(..., description="Bounding box coordinates")
    confidence: float = Field(..., ge=0.0, le=1.0, description="OCR confidence score")
    page: int = Field(..., ge=0, description="Page number (0-indexed)")


class OCRResult(BaseModel):
    tokens: List[OCRToken] = Field(..., description="List of OCR tokens")
    page_count: int = Field(..., description="Total number of pages")
    processing_time: float = Field(..., description="OCR processing time in seconds")


class TemplateMatch(BaseModel):
    template_id: str = Field(..., description="Matched template identifier")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Template match confidence")
    matched_keywords: List[str] = Field(..., description="Keywords that matched")
    is_match: bool = Field(..., description="Whether template matched")


class CurrencyAmount(BaseModel):
    value: float = Field(..., description="Monetary amount")
    currency: str = Field(..., description="Currency code (ISO 4217)")


class ExtractedField(BaseModel):
    field_name: str = Field(..., description="Name of the extracted field")
    value: Union[str, float, int, CurrencyAmount, datetime] = Field(..., description="Extracted value")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Extraction confidence")
    confidence_level: ConfidenceLevel = Field(..., description="Confidence level category")
    source_tokens: List[OCRToken] = Field(..., description="Source OCR tokens")
    extraction_method: str = Field(..., description="Method used for extraction (rule-based/layoutlm)")


class DocumentExtraction(BaseModel):
    document_id: str = Field(..., description="Unique document identifier")
    filename: str = Field(..., description="Original filename")
    extracted_fields: List[ExtractedField] = Field(..., description="All extracted fields")
    template_match: Optional[TemplateMatch] = Field(None, description="Template matching result")
    processing_metadata: Dict[str, Any] = Field(..., description="Processing metadata")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")


class InsuranceSubmission(BaseModel):
    """Standard insurance submission output schema"""
    unique_market_reference: Optional[str] = Field(None, description="UMR identifier")
    type_of_insurance: Optional[str] = Field(None, description="Insurance type")
    named_insured: Optional[str] = Field(None, description="Named insured party")
    policy_period_start: Optional[str] = Field(None, description="Policy start date (ISO 8601)")
    policy_period_end: Optional[str] = Field(None, description="Policy end date (ISO 8601)")
    amount_of_insurance: Optional[CurrencyAmount] = Field(None, description="Insurance amount")
    confidence_metrics: Dict[str, Any] = Field(..., description="Confidence metrics")


class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ProcessingJob(BaseModel):
    job_id: str = Field(..., description="Unique job identifier")
    filename: str = Field(..., description="Original filename")
    status: ProcessingStatus = Field(..., description="Current processing status")
    created_at: datetime = Field(default_factory=datetime.now, description="Job creation time")
    completed_at: Optional[datetime] = Field(None, description="Job completion time")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    result: Optional[DocumentExtraction] = Field(None, description="Processing result")


class ServiceHealth(BaseModel):
    service_name: str = Field(..., description="Service name")
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Service version")
    timestamp: datetime = Field(default_factory=datetime.now, description="Health check timestamp")


class LogEntry(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.now, description="Log timestamp")
    level: str = Field(..., description="Log level")
    service: str = Field(..., description="Service name")
    message: str = Field(..., description="Log message")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")