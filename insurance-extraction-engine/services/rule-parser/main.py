import os
import re
import time
import yaml
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from dateutil import parser as date_parser
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from loguru import logger

app = FastAPI(title="Rule-based Parser Service", version="1.0.0")

# Configure logging
logger.add("logs/rule_parser.log", rotation="10 MB")
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


class TemplateMatch(BaseModel):
    template_id: str
    confidence: float
    matched_keywords: List[str]
    is_match: bool
    match_details: Dict[str, Any]


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


class RuleParsingRequest(BaseModel):
    job_id: str
    tokens: List[OCRToken]
    template_match: TemplateMatch
    page_count: int


class RuleParsingResult(BaseModel):
    job_id: str
    extracted_fields: List[ExtractedField]
    processing_time: float
    status: str
    template_used: str


# Load parsing rules
def load_parsing_rules():
    """Load parsing rules from YAML files"""
    rules = {}
    rules_dir = "/app/data/templates"
    
    if not os.path.exists(rules_dir):
        os.makedirs(rules_dir, exist_ok=True)
        create_default_rules(rules_dir)
    
    for filename in os.listdir(rules_dir):
        if filename.endswith('_rules.yaml') or filename.endswith('_rules.yml'):
            rules_path = os.path.join(rules_dir, filename)
            try:
                with open(rules_path, 'r') as f:
                    rules_data = yaml.safe_load(f)
                    template_id = filename.replace('_rules.yaml', '').replace('_rules.yml', '')
                    rules[template_id] = rules_data
                    logger.info(f"Loaded parsing rules: {template_id}")
            except Exception as e:
                logger.error(f"Error loading rules {filename}: {str(e)}")
    
    return rules


def create_default_rules(rules_dir):
    """Create default parsing rules for insurance templates"""
    
    # Standard insurance parsing rules
    standard_rules = {
        "fields": {
            "unique_market_reference": {
                "patterns": [
                    r"(?:unique market reference|umr)[\s:]*([A-Z0-9]{10,20})",
                    r"umr[\s:]*([A-Z0-9]{10,20})",
                    r"reference[\s:]*([A-Z0-9]{10,20})"
                ],
                "anchor_keywords": ["unique market reference", "umr", "reference"],
                "search_radius": {"x": 0.5, "y": 0.1},
                "value_type": "string",
                "required": True
            },
            "type_of_insurance": {
                "patterns": [
                    r"(?:type of insurance|insurance type)[\s:]*([^\\n\\r]{5,50})",
                    r"coverage[\s:]*([^\\n\\r]{5,50})"
                ],
                "anchor_keywords": ["type of insurance", "insurance type", "coverage"],
                "search_radius": {"x": 0.5, "y": 0.1},
                "value_type": "string",
                "required": True
            },
            "named_insured": {
                "patterns": [
                    r"(?:named insured|insured)[\s:]*([^\\n\\r]{5,100})",
                    r"policyholder[\s:]*([^\\n\\r]{5,100})"
                ],
                "anchor_keywords": ["named insured", "insured", "policyholder"],
                "search_radius": {"x": 0.5, "y": 0.1},
                "value_type": "string",
                "required": True
            },
            "policy_period_start": {
                "patterns": [
                    r"(?:policy period|period)[\s:]*(?:from[\s:]*)?([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})",
                    r"(?:effective|start)[\s:]*([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})",
                    r"from[\s:]*([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})"
                ],
                "anchor_keywords": ["policy period", "effective", "start", "from"],
                "search_radius": {"x": 0.5, "y": 0.1},
                "value_type": "date",
                "required": True
            },
            "policy_period_end": {
                "patterns": [
                    r"(?:to|until|end)[\s:]*([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})",
                    r"expir[ey][\s:]*([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})"
                ],
                "anchor_keywords": ["to", "until", "end", "expiry"],
                "search_radius": {"x": 0.5, "y": 0.1},
                "value_type": "date",
                "required": True
            },
            "amount_of_insurance": {
                "patterns": [
                    r"(?:amount of insurance|sum insured|limit)[\s:]*([A-Z]{3}[\s]*[0-9,]+(?:\.[0-9]{2})?)",
                    r"([A-Z]{3}[\s]*[0-9,]+(?:\.[0-9]{2})?)[\s]*(?:amount|sum|limit)"
                ],
                "anchor_keywords": ["amount of insurance", "sum insured", "limit"],
                "search_radius": {"x": 0.5, "y": 0.1},
                "value_type": "currency",
                "required": True
            }
        }
    }
    
    # Launch & orbit insurance parsing rules
    launch_rules = {
        "fields": {
            "unique_market_reference": {
                "patterns": [
                    r"(?:unique market reference|umr)[\s:]*([A-Z0-9]{10,20})",
                    r"umr[\s:]*([A-Z0-9]{10,20})"
                ],
                "anchor_keywords": ["unique market reference", "umr"],
                "search_radius": {"x": 0.5, "y": 0.1},
                "value_type": "string",
                "required": True
            },
            "type_of_insurance": {
                "patterns": [
                    r"(?:launch.*orbit|satellite.*insurance|space.*insurance)",
                    r"(?:type of insurance)[\s:]*([^\\n\\r]*(?:launch|orbit|satellite|space)[^\\n\\r]*)"
                ],
                "anchor_keywords": ["type of insurance", "launch", "orbit", "satellite"],
                "search_radius": {"x": 0.5, "y": 0.1},
                "value_type": "string",
                "required": True
            },
            "named_insured": {
                "patterns": [
                    r"(?:named insured|insured)[\s:]*([^\\n\\r]{5,100})",
                    r"satellite owner[\s:]*([^\\n\\r]{5,100})"
                ],
                "anchor_keywords": ["named insured", "insured", "satellite owner"],
                "search_radius": {"x": 0.5, "y": 0.1},
                "value_type": "string",
                "required": True
            },
            "launch_date": {
                "patterns": [
                    r"(?:launch date|launch)[\s:]*([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})",
                    r"scheduled launch[\s:]*([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})"
                ],
                "anchor_keywords": ["launch date", "launch", "scheduled launch"],
                "search_radius": {"x": 0.5, "y": 0.1},
                "value_type": "date",
                "required": True
            },
            "amount_of_insurance": {
                "patterns": [
                    r"(?:amount of insurance|sum insured|limit)[\s:]*([A-Z]{3}[\s]*[0-9,]+(?:\.[0-9]{2})?)",
                    r"([A-Z]{3}[\s]*[0-9,]+(?:\.[0-9]{2})?)[\s]*(?:amount|sum|limit)"
                ],
                "anchor_keywords": ["amount of insurance", "sum insured", "limit"],
                "search_radius": {"x": 0.5, "y": 0.1},
                "value_type": "currency",
                "required": True
            }
        }
    }
    
    # Save rules
    with open(os.path.join(rules_dir, "standard_insurance_rules.yaml"), 'w') as f:
        yaml.dump(standard_rules, f, default_flow_style=False)
    
    with open(os.path.join(rules_dir, "launch_orbit_insurance_rules.yaml"), 'w') as f:
        yaml.dump(launch_rules, f, default_flow_style=False)
    
    logger.info("Created default parsing rules")


# Global rules cache
rules_cache = None


def get_parsing_rules():
    """Get parsing rules with caching"""
    global rules_cache
    if rules_cache is None:
        rules_cache = load_parsing_rules()
    return rules_cache


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "service": "rule-parser",
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": time.time(),
        "rules_loaded": len(get_parsing_rules())
    }


def find_tokens_near_anchor(tokens: List[OCRToken], anchor_keywords: List[str], 
                          search_radius: Dict[str, float]) -> List[OCRToken]:
    """Find tokens near anchor keywords within search radius"""
    
    anchor_tokens = []
    # Find anchor tokens
    for token in tokens:
        for keyword in anchor_keywords:
            if keyword.lower() in token.text.lower():
                anchor_tokens.append(token)
                break
    
    if not anchor_tokens:
        return []
    
    # Find tokens within search radius of any anchor
    nearby_tokens = []
    for token in tokens:
        for anchor in anchor_tokens:
            # Calculate distance
            x_dist = abs(token.bbox.x1 - anchor.bbox.x2)  # Distance from anchor end
            y_dist = abs(token.bbox.y1 - anchor.bbox.y1)  # Vertical distance
            
            if x_dist <= search_radius["x"] and y_dist <= search_radius["y"]:
                nearby_tokens.append(token)
                break
    
    return nearby_tokens


def extract_with_pattern(tokens: List[OCRToken], patterns: List[str]) -> Optional[Dict[str, Any]]:
    """Extract value using regex patterns"""
    
    # Combine all token text
    full_text = " ".join([token.text for token in tokens])
    
    for pattern in patterns:
        try:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                # Find which tokens contributed to this match
                match_start = match.start()
                match_end = match.end()
                
                # Calculate character positions in combined text
                char_pos = 0
                source_tokens = []
                
                for token in tokens:
                    token_start = char_pos
                    token_end = char_pos + len(token.text)
                    
                    # Check if this token overlaps with the match
                    if not (token_end < match_start or token_start > match_end):
                        source_tokens.append(token)
                    
                    char_pos = token_end + 1  # +1 for space
                
                return {
                    "value": match.group(1) if match.groups() else match.group(0),
                    "full_match": match.group(0),
                    "source_tokens": source_tokens,
                    "pattern": pattern
                }
        except Exception as e:
            logger.warning(f"Pattern matching error: {str(e)}")
            continue
    
    return None


def normalize_value(raw_value: str, value_type: str) -> Union[str, float, int, CurrencyAmount, datetime]:
    """Normalize extracted value based on type"""
    
    if value_type == "string":
        return raw_value.strip()
    
    elif value_type == "date":
        try:
            # Try to parse date
            parsed_date = date_parser.parse(raw_value, fuzzy=True)
            return parsed_date.strftime("%Y-%m-%d")
        except:
            return raw_value.strip()
    
    elif value_type == "currency":
        try:
            # Extract currency and amount
            # Pattern: EUR 1,000,000.00 or 1,000,000.00 EUR
            currency_match = re.search(r'([A-Z]{3})', raw_value)
            amount_match = re.search(r'([0-9,]+(?:\.[0-9]{2})?)', raw_value)
            
            if currency_match and amount_match:
                currency = currency_match.group(1)
                amount_str = amount_match.group(1).replace(',', '')
                amount = float(amount_str)
                
                return CurrencyAmount(value=amount, currency=currency)
            else:
                return raw_value.strip()
        except:
            return raw_value.strip()
    
    elif value_type == "number":
        try:
            # Remove commas and convert to float
            clean_value = raw_value.replace(',', '')
            if '.' in clean_value:
                return float(clean_value)
            else:
                return int(clean_value)
        except:
            return raw_value.strip()
    
    return raw_value.strip()


def calculate_confidence(source_tokens: List[OCRToken], extraction_method: str) -> float:
    """Calculate confidence based on source tokens and method"""
    
    if not source_tokens:
        return 0.0
    
    # Average OCR confidence
    avg_ocr_confidence = sum(token.confidence for token in source_tokens) / len(source_tokens)
    
    # Method confidence (rule-based is generally high if pattern matches)
    method_confidence = 0.9 if extraction_method == "rule-based" else 0.7
    
    # Combined confidence
    return (avg_ocr_confidence * 0.6) + (method_confidence * 0.4)


def get_confidence_level(confidence: float) -> str:
    """Get confidence level category"""
    if confidence >= 0.90:
        return "high"
    elif confidence >= 0.75:
        return "medium"
    else:
        return "low"


def extract_field(tokens: List[OCRToken], field_name: str, field_config: Dict[str, Any]) -> Optional[ExtractedField]:
    """Extract a single field using rule-based approach"""
    
    patterns = field_config.get("patterns", [])
    anchor_keywords = field_config.get("anchor_keywords", [])
    search_radius = field_config.get("search_radius", {"x": 0.5, "y": 0.1})
    value_type = field_config.get("value_type", "string")
    
    # Find tokens near anchor keywords
    if anchor_keywords:
        candidate_tokens = find_tokens_near_anchor(tokens, anchor_keywords, search_radius)
        if not candidate_tokens:
            # Fallback to all tokens if no anchors found
            candidate_tokens = tokens
    else:
        candidate_tokens = tokens
    
    # Try to extract using patterns
    extraction_result = extract_with_pattern(candidate_tokens, patterns)
    
    if not extraction_result:
        return None
    
    # Normalize the value
    normalized_value = normalize_value(extraction_result["value"], value_type)
    
    # Calculate confidence
    confidence = calculate_confidence(extraction_result["source_tokens"], "rule-based")
    
    return ExtractedField(
        field_name=field_name,
        value=normalized_value,
        confidence=confidence,
        confidence_level=get_confidence_level(confidence),
        source_tokens=extraction_result["source_tokens"],
        extraction_method="rule-based"
    )


@app.post("/parse", response_model=RuleParsingResult)
async def parse_fields(request: RuleParsingRequest):
    """
    Parse fields from OCR tokens using rule-based extraction
    """
    start_time = time.time()
    
    try:
        logger.info(f"Starting rule-based parsing for job {request.job_id} using template {request.template_match.template_id}")
        
        # Get parsing rules for the matched template
        parsing_rules = get_parsing_rules()
        template_rules = parsing_rules.get(request.template_match.template_id)
        
        if not template_rules:
            raise HTTPException(status_code=404, detail=f"No parsing rules found for template {request.template_match.template_id}")
        
        extracted_fields = []
        fields_config = template_rules.get("fields", {})
        
        # Extract each field
        for field_name, field_config in fields_config.items():
            try:
                extracted_field = extract_field(request.tokens, field_name, field_config)
                if extracted_field:
                    extracted_fields.append(extracted_field)
                elif field_config.get("required", False):
                    logger.warning(f"Required field '{field_name}' not found for job {request.job_id}")
            except Exception as e:
                logger.error(f"Error extracting field '{field_name}' for job {request.job_id}: {str(e)}")
        
        processing_time = time.time() - start_time
        
        result = RuleParsingResult(
            job_id=request.job_id,
            extracted_fields=extracted_fields,
            processing_time=processing_time,
            status="completed",
            template_used=request.template_match.template_id
        )
        
        logger.info(f"Rule-based parsing completed for job {request.job_id}: "
                   f"extracted {len(extracted_fields)} fields in {processing_time:.2f}s")
        
        return result
        
    except Exception as e:
        logger.error(f"Error during rule-based parsing for job {request.job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Rule-based parsing failed: {str(e)}")


@app.post("/reload_rules")
async def reload_rules():
    """Reload parsing rules from disk"""
    global rules_cache
    rules_cache = None
    rules = get_parsing_rules()
    
    return {
        "status": "rules_reloaded",
        "rules_count": len(rules),
        "templates": list(rules.keys())
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)