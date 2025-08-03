#!/bin/bash

# Insurance Submission Extraction Engine Startup Script

echo "🚀 Starting Insurance Submission Extraction Engine..."
echo "======================================================"

# Check if Docker and Docker Compose are available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data/templates data/samples
mkdir -p outputs/extracted_data outputs/confidence_metrics outputs/rendered_pages outputs/logs
mkdir -p models

# Set permissions
chmod -R 755 data outputs models

# Build and start services
echo "🏗️  Building and starting services..."
docker-compose up --build -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 30

# Check service health
echo "🔍 Checking service health..."

services=("pdf-renderer:8001" "paddleocr:8002" "template-matcher:8003" "rule-parser:8004" "layoutlm:8005" "normalizer:8006" "storage:8007" "logger:8008")

all_healthy=true

for service in "${services[@]}"; do
    name=${service%:*}
    port=${service#*:}
    
    echo -n "  Checking $name... "
    
    if curl -s "http://localhost:$port/health" > /dev/null; then
        echo "✅ Healthy"
    else
        echo "❌ Not responding"
        all_healthy=false
    fi
done

echo ""

if [ "$all_healthy" = true ]; then
    echo "🎉 All services are healthy!"
    echo ""
    echo "🌐 Web Interface: http://localhost:8501"
    echo "📚 API Documentation:"
    echo "   - PDF Renderer: http://localhost:8001/docs"
    echo "   - PaddleOCR: http://localhost:8002/docs"
    echo "   - Template Matcher: http://localhost:8003/docs"
    echo "   - Rule Parser: http://localhost:8004/docs"
    echo "   - LayoutLM: http://localhost:8005/docs"
    echo "   - Normalizer: http://localhost:8006/docs"
    echo "   - Storage: http://localhost:8007/docs"
    echo "   - Logger: http://localhost:8008/docs"
    echo ""
    echo "📖 For more information, see README.md"
else
    echo "⚠️  Some services are not responding. Check logs with:"
    echo "   docker-compose logs <service-name>"
    echo ""
    echo "🔧 To restart services:"
    echo "   docker-compose restart"
fi

echo ""
echo "🛑 To stop all services:"
echo "   docker-compose down"