# Insurance Submission Extraction Engine

A fully containerized, modular document processing engine that extracts structured data from insurance submissions using layout-aware OCR and field classification.

## 🎯 Overview

This system processes PDF insurance documents through a microservices architecture, extracting key fields using both rule-based parsing for known templates and LayoutLMv3 for unknown layouts. It provides a user-friendly Streamlit interface with confidence visualization and structured JSON output.

## 🏗 Architecture

### Microservices

| Service | Port | Description |
|---------|------|-------------|
| **PDF Renderer** | 8001 | Converts PDFs to 300 DPI images |
| **PaddleOCR** | 8002 | Extracts text with bounding boxes and confidence |
| **Template Matcher** | 8003 | Matches documents against known templates |
| **Rule Parser** | 8004 | Extracts fields using rule-based patterns |
| **LayoutLM** | 8005 | AI-powered extraction for unknown layouts |
| **Normalizer** | 8006 | Post-processes and validates outputs |
| **Storage** | 8007 | Manages result storage and retrieval |
| **Logger** | 8008 | Centralized audit logging and metrics |
| **Web App** | 8501 | Streamlit user interface |

### Data Flow

```
PDF Upload → PDF Renderer → PaddleOCR → Template Matcher
                                              ↓
                                        Known Template?
                                         ↙         ↘
                                Rule Parser    LayoutLM Service
                                         ↘         ↙
                                      Normalizer → Storage
                                              ↓
                                        Web Interface
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- At least 8GB RAM (for LayoutLM service)
- 10GB free disk space

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd insurance-extraction-engine
   ```

2. **Build and start services**
   ```bash
   docker-compose up --build
   ```

3. **Access the application**
   - Web Interface: http://localhost:8501
   - API Documentation: http://localhost:800X/docs (replace X with service port)

### First Run

1. Open http://localhost:8501 in your browser
2. Check service health in the sidebar
3. Upload a PDF insurance document
4. Click "Process Document" and wait for completion
5. View results in the "Results" and "Analysis" tabs

## 📄 Supported Document Types

### Built-in Templates

1. **Standard Insurance Submission**
   - Unique Market Reference (UMR)
   - Named Insured
   - Policy Period
   - Amount of Insurance
   - Type of Insurance

2. **Launch & In Orbit Insurance**
   - Satellite/spacecraft details
   - Launch date
   - Mission parameters
   - Coverage amounts

### Custom Templates

Add new templates by creating YAML files in `data/templates/`:

```yaml
# data/templates/my_template.yaml
name: "My Custom Template"
description: "Custom insurance template"
required_keywords:
  - "policy number"
  - "coverage amount"
optional_keywords:
  - "deductible"
  - "premium"
layout_anchors:
  - keyword: "policy number"
    expected_position: {"x": 0.1, "y": 0.2, "tolerance": 0.3}
    weight: 3.0
confidence_thresholds:
  keyword_match: 0.7
  layout_match: 0.6
  overall_match: 0.75
```

## 🔧 Configuration

### Environment Variables

```bash
# Service URLs (automatically configured in Docker Compose)
PDF_RENDERER_URL=http://pdf-renderer:8000
PADDLEOCR_URL=http://paddleocr:8000
TEMPLATE_MATCHER_URL=http://template-matcher:8000
RULE_PARSER_URL=http://rule-parser:8000
LAYOUTLM_URL=http://layoutlm:8000
NORMALIZER_URL=http://normalizer:8000
STORAGE_URL=http://storage:8000
LOGGER_URL=http://logger:8000

# Logging
LOG_LEVEL=INFO
```

### Volume Mounts

- `./data` → Template definitions and sample files
- `./outputs` → Processed results and logs
- `./models` → LayoutLM model cache

## 📊 Output Schema

### Standard Insurance Submission

```json
{
  "unique_market_reference": "UMR123456789A",
  "type_of_insurance": "Launch & In Orbit Insurance",
  "named_insured": "ACME Satellite Co.",
  "policy_period_start": "2024-12-31",
  "policy_period_end": "2026-12-31",
  "amount_of_insurance": {
    "value": 100000000,
    "currency": "EUR"
  },
  "confidence_metrics": {
    "average_confidence": 0.91,
    "fields": {
      "named_insured": 0.95,
      "amount_of_insurance": 0.88
    }
  }
}
```

### Confidence Levels

- **High**: ≥ 0.90 - Highly reliable extraction
- **Medium**: 0.75-0.89 - Good confidence, may need review
- **Low**: < 0.75 - Requires human verification

## 🛠 Development

### Adding New Services

1. Create service directory: `services/my-service/`
2. Add Dockerfile and requirements.txt
3. Implement FastAPI application with `/health` endpoint
4. Update docker-compose.yml
5. Add service URL to webapp environment

### Custom Field Extraction Rules

Create parsing rules in `data/templates/my_template_rules.yaml`:

```yaml
fields:
  policy_number:
    patterns:
      - "(?:policy number|policy no)[\s:]*([A-Z0-9]{8,20})"
    anchor_keywords: ["policy number", "policy no"]
    search_radius: {"x": 0.5, "y": 0.1}
    value_type: "string"
    required: true
```

### Testing

```bash
# Run individual service tests
cd services/pdf-renderer
python -m pytest tests/

# Integration tests
docker-compose -f docker-compose.test.yml up --build
```

## 📈 Monitoring

### Health Checks

All services expose `/health` endpoints:

```bash
curl http://localhost:8001/health  # PDF Renderer
curl http://localhost:8002/health  # PaddleOCR
# ... etc
```

### Logs

- Service logs: `outputs/logs/`
- Structured audit logs via Logger service
- Query logs: POST to http://localhost:8008/query

### Metrics

- Processing times per service
- OCR confidence distributions
- Template matching statistics
- Error rates and service availability

## 🔍 Troubleshooting

### Common Issues

1. **Services not starting**
   ```bash
   docker-compose logs <service-name>
   docker-compose ps
   ```

2. **Memory issues**
   - Increase Docker memory limit to 8GB+
   - Disable LayoutLM service if not needed

3. **OCR quality issues**
   - Ensure PDFs are high quality (300+ DPI)
   - Check image rendering quality
   - Adjust confidence thresholds

4. **Template matching fails**
   - Review template keywords and anchors
   - Check document structure matches expectations
   - Add debug logging to template matcher

### Performance Optimization

- **PDF Rendering**: Use smaller DPI for faster processing
- **OCR**: Adjust confidence thresholds to balance speed/accuracy
- **Template Matching**: Optimize keyword lists and layout anchors
- **Storage**: Use database instead of file storage for production

## 🔒 Security Considerations

- Services run in isolated containers
- No external network dependencies
- File uploads are validated and scoped
- Audit logging for all operations
- Consider adding authentication for production use

## 📋 API Documentation

Each service provides OpenAPI documentation at `/docs`:

- PDF Renderer: http://localhost:8001/docs
- PaddleOCR: http://localhost:8002/docs
- Template Matcher: http://localhost:8003/docs
- Rule Parser: http://localhost:8004/docs
- Storage: http://localhost:8007/docs
- Logger: http://localhost:8008/docs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all services build and run
5. Update documentation
6. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:

1. Check the troubleshooting section
2. Review service logs
3. Create an issue with:
   - Error messages
   - Service logs
   - Sample document (if possible)
   - Environment details

---

**Built with**: Python, FastAPI, Streamlit, PaddleOCR, Docker, and ❤️