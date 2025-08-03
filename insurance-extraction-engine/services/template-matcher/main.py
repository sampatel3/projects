import os
import time
import yaml
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fuzzywuzzy import fuzz
from loguru import logger

app = FastAPI(title="Template Matcher Service", version="1.0.0")

# Configure logging
logger.add("logs/template_matcher.log", rotation="10 MB")
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


class TemplateMatchRequest(BaseModel):
    job_id: str
    tokens: List[OCRToken]
    page_count: int


class TemplateMatch(BaseModel):
    template_id: str
    confidence: float
    matched_keywords: List[str]
    is_match: bool
    match_details: Dict[str, Any]


class TemplateMatchResult(BaseModel):
    job_id: str
    best_match: Optional[TemplateMatch]
    all_matches: List[TemplateMatch]
    processing_time: float
    status: str


# Load template definitions
def load_templates():
    """Load template definitions from YAML files"""
    templates = {}
    templates_dir = "/app/data/templates"
    
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir, exist_ok=True)
        # Create default template
        create_default_templates(templates_dir)
    
    for filename in os.listdir(templates_dir):
        if filename.endswith('.yaml') or filename.endswith('.yml'):
            template_path = os.path.join(templates_dir, filename)
            try:
                with open(template_path, 'r') as f:
                    template_data = yaml.safe_load(f)
                    template_id = os.path.splitext(filename)[0]
                    templates[template_id] = template_data
                    logger.info(f"Loaded template: {template_id}")
            except Exception as e:
                logger.error(f"Error loading template {filename}: {str(e)}")
    
    return templates


def create_default_templates(templates_dir):
    """Create default insurance template definitions"""
    
    # Standard insurance submission template
    standard_template = {
        "name": "Standard Insurance Submission",
        "description": "Standard insurance submission form template",
        "required_keywords": [
            "unique market reference",
            "umr",
            "type of insurance",
            "named insured",
            "policy period",
            "amount of insurance"
        ],
        "optional_keywords": [
            "broker",
            "underwriter",
            "deductible",
            "premium",
            "coverage"
        ],
        "layout_anchors": [
            {
                "keyword": "unique market reference",
                "expected_position": {"x": 0.1, "y": 0.2, "tolerance": 0.3},
                "weight": 3.0
            },
            {
                "keyword": "named insured",
                "expected_position": {"x": 0.1, "y": 0.3, "tolerance": 0.3},
                "weight": 2.0
            },
            {
                "keyword": "policy period",
                "expected_position": {"x": 0.1, "y": 0.5, "tolerance": 0.3},
                "weight": 2.0
            }
        ],
        "confidence_thresholds": {
            "keyword_match": 0.7,
            "layout_match": 0.6,
            "overall_match": 0.75
        }
    }
    
    # Launch & In Orbit Insurance template
    launch_template = {
        "name": "Launch & In Orbit Insurance",
        "description": "Satellite launch and in-orbit insurance template",
        "required_keywords": [
            "launch",
            "orbit",
            "satellite",
            "spacecraft",
            "mission",
            "launch date"
        ],
        "optional_keywords": [
            "payload",
            "launcher",
            "ground risk",
            "third party liability",
            "mission duration"
        ],
        "layout_anchors": [
            {
                "keyword": "launch date",
                "expected_position": {"x": 0.1, "y": 0.4, "tolerance": 0.3},
                "weight": 3.0
            },
            {
                "keyword": "satellite",
                "expected_position": {"x": 0.1, "y": 0.2, "tolerance": 0.3},
                "weight": 2.0
            }
        ],
        "confidence_thresholds": {
            "keyword_match": 0.6,
            "layout_match": 0.5,
            "overall_match": 0.65
        }
    }
    
    # Save templates
    with open(os.path.join(templates_dir, "standard_insurance.yaml"), 'w') as f:
        yaml.dump(standard_template, f, default_flow_style=False)
    
    with open(os.path.join(templates_dir, "launch_orbit_insurance.yaml"), 'w') as f:
        yaml.dump(launch_template, f, default_flow_style=False)
    
    logger.info("Created default templates")


# Global templates cache
templates_cache = None


def get_templates():
    """Get templates with caching"""
    global templates_cache
    if templates_cache is None:
        templates_cache = load_templates()
    return templates_cache


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "service": "template-matcher",
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": time.time(),
        "templates_loaded": len(get_templates())
    }


@app.get("/templates")
async def list_templates():
    """List available templates"""
    templates = get_templates()
    return {
        "templates": [
            {
                "id": template_id,
                "name": template_data.get("name", template_id),
                "description": template_data.get("description", "")
            }
            for template_id, template_data in templates.items()
        ]
    }


def calculate_keyword_match(tokens: List[OCRToken], template: Dict) -> Dict[str, Any]:
    """Calculate keyword matching score for a template"""
    
    # Extract all text from tokens
    all_text = " ".join([token.text.lower() for token in tokens])
    
    required_keywords = template.get("required_keywords", [])
    optional_keywords = template.get("optional_keywords", [])
    
    matched_required = []
    matched_optional = []
    
    # Check required keywords
    for keyword in required_keywords:
        keyword_lower = keyword.lower()
        # Use fuzzy matching
        best_match_score = 0
        for token in tokens:
            score = fuzz.partial_ratio(keyword_lower, token.text.lower())
            if score > best_match_score:
                best_match_score = score
        
        if best_match_score >= 70:  # 70% fuzzy match threshold
            matched_required.append(keyword)
    
    # Check optional keywords
    for keyword in optional_keywords:
        keyword_lower = keyword.lower()
        best_match_score = 0
        for token in tokens:
            score = fuzz.partial_ratio(keyword_lower, token.text.lower())
            if score > best_match_score:
                best_match_score = score
        
        if best_match_score >= 70:
            matched_optional.append(keyword)
    
    # Calculate scores
    required_score = len(matched_required) / len(required_keywords) if required_keywords else 1.0
    optional_score = len(matched_optional) / len(optional_keywords) if optional_keywords else 0.0
    
    # Weighted average (required keywords are more important)
    keyword_confidence = (required_score * 0.8) + (optional_score * 0.2)
    
    return {
        "keyword_confidence": keyword_confidence,
        "matched_required": matched_required,
        "matched_optional": matched_optional,
        "required_score": required_score,
        "optional_score": optional_score
    }


def calculate_layout_match(tokens: List[OCRToken], template: Dict) -> Dict[str, Any]:
    """Calculate layout matching score for a template"""
    
    layout_anchors = template.get("layout_anchors", [])
    if not layout_anchors:
        return {"layout_confidence": 0.5, "matched_anchors": []}
    
    matched_anchors = []
    total_weight = 0
    matched_weight = 0
    
    for anchor in layout_anchors:
        keyword = anchor["keyword"].lower()
        expected_pos = anchor["expected_position"]
        tolerance = expected_pos.get("tolerance", 0.3)
        weight = anchor.get("weight", 1.0)
        
        total_weight += weight
        
        # Find tokens that match this keyword
        for token in tokens:
            if fuzz.partial_ratio(keyword, token.text.lower()) >= 70:
                # Check if position is within tolerance
                x_diff = abs(token.bbox.x1 - expected_pos["x"])
                y_diff = abs(token.bbox.y1 - expected_pos["y"])
                
                if x_diff <= tolerance and y_diff <= tolerance:
                    matched_anchors.append({
                        "keyword": keyword,
                        "expected": expected_pos,
                        "actual": {"x": token.bbox.x1, "y": token.bbox.y1},
                        "weight": weight
                    })
                    matched_weight += weight
                    break
    
    layout_confidence = matched_weight / total_weight if total_weight > 0 else 0.0
    
    return {
        "layout_confidence": layout_confidence,
        "matched_anchors": matched_anchors,
        "total_anchors": len(layout_anchors),
        "matched_anchor_count": len(matched_anchors)
    }


def match_template(tokens: List[OCRToken], template_id: str, template: Dict) -> TemplateMatch:
    """Match tokens against a specific template"""
    
    # Calculate keyword matching
    keyword_match = calculate_keyword_match(tokens, template)
    
    # Calculate layout matching
    layout_match = calculate_layout_match(tokens, template)
    
    # Get confidence thresholds
    thresholds = template.get("confidence_thresholds", {})
    keyword_threshold = thresholds.get("keyword_match", 0.7)
    layout_threshold = thresholds.get("layout_match", 0.6)
    overall_threshold = thresholds.get("overall_match", 0.75)
    
    # Calculate overall confidence (weighted average)
    overall_confidence = (
        keyword_match["keyword_confidence"] * 0.7 +
        layout_match["layout_confidence"] * 0.3
    )
    
    # Determine if this is a match
    is_match = (
        keyword_match["keyword_confidence"] >= keyword_threshold and
        layout_match["layout_confidence"] >= layout_threshold and
        overall_confidence >= overall_threshold
    )
    
    # Collect all matched keywords
    all_matched = keyword_match["matched_required"] + keyword_match["matched_optional"]
    
    return TemplateMatch(
        template_id=template_id,
        confidence=overall_confidence,
        matched_keywords=all_matched,
        is_match=is_match,
        match_details={
            "keyword_match": keyword_match,
            "layout_match": layout_match,
            "thresholds": thresholds
        }
    )


@app.post("/match", response_model=TemplateMatchResult)
async def match_templates(request: TemplateMatchRequest):
    """
    Match OCR tokens against known templates
    Returns the best matching template or None if no match found
    """
    start_time = time.time()
    
    try:
        logger.info(f"Starting template matching for job {request.job_id}")
        
        templates = get_templates()
        all_matches = []
        
        # Test each template
        for template_id, template_data in templates.items():
            match = match_template(request.tokens, template_id, template_data)
            all_matches.append(match)
        
        # Sort by confidence
        all_matches.sort(key=lambda x: x.confidence, reverse=True)
        
        # Find best match (if any)
        best_match = None
        for match in all_matches:
            if match.is_match:
                best_match = match
                break
        
        processing_time = time.time() - start_time
        
        result = TemplateMatchResult(
            job_id=request.job_id,
            best_match=best_match,
            all_matches=all_matches,
            processing_time=processing_time,
            status="completed"
        )
        
        if best_match:
            logger.info(f"Template match found for job {request.job_id}: "
                       f"{best_match.template_id} (confidence: {best_match.confidence:.3f})")
        else:
            logger.info(f"No template match found for job {request.job_id}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error during template matching for job {request.job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Template matching failed: {str(e)}")


@app.post("/reload_templates")
async def reload_templates():
    """Reload templates from disk"""
    global templates_cache
    templates_cache = None
    templates = get_templates()
    
    return {
        "status": "templates_reloaded",
        "templates_count": len(templates),
        "templates": list(templates.keys())
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)