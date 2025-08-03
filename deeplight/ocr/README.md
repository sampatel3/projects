# Multi-Engine OCR PDF Visualizer

A powerful OCR application supporting multiple OCR engines with GPU acceleration for faster PDF text extraction and visualization.

## 🚀 Key Features

- **Multiple OCR Engines**: Choose between EasyOCR, DocTR, and PaddleOCR
- **GPU Acceleration**: Mac GPU support through Metal Performance Shaders (MPS) 
- **Smart Page Selection**: Select specific pages or ranges to process
- **Interactive Processing**: Process button with real-time control
- **Performance Metrics**: Detailed timing and processing statistics
- **Model Comparison**: Easy switching between different OCR models
- **JSON Export**: Complete OCR results with metadata and model information

## 🤖 Available OCR Models

### EasyOCR ✅ Recommended
- **GPU Support**: ✅ Full Metal Performance Shaders acceleration
- **Accuracy**: Excellent text recognition
- **Speed**: 2-5x faster on GPU
- **Best for**: General OCR tasks, high accuracy text extraction

### EasyOCR + LayoutLMv3 ✅ Recommended for Documents
- **GPU Support**: ✅ Full GPU acceleration
- **Accuracy**: Excellent + document understanding
- **Speed**: 2-4x faster on GPU
- **Best for**: Structured documents, forms, complex layouts

### Donut
- **GPU Support**: ✅ Full GPU acceleration
- **Accuracy**: Good for document understanding
- **Speed**: 1-3x faster on GPU
- **Best for**: OCR-free document analysis, experimental use

## 🔄 New Workflow

1. **Select OCR Model**: Choose between EasyOCR, EasyOCR + LayoutLMv3, or Donut
2. **Upload PDF**: Load your document
3. **Select Pages**: Choose specific pages or use quick selection
4. **Process**: Click the process button to start OCR
5. **Review Results**: View results with bounding boxes and confidence scores
6. **Export**: Download JSON with model and performance data

## 📋 Requirements

- **macOS**: 10.15+ (for Metal support)
- **Python**: 3.8+
- **Mac with Apple Silicon or Intel GPU**: For GPU acceleration
- **Memory**: 4GB+ RAM recommended

## 🛠 Installation

### Option 1: Automated Setup (Recommended)
```bash
cd deeplight/ocr
python setup_gpu.py
```

### Option 2: Manual Setup
```bash
# Install PyTorch with Metal support
pip install torch>=2.0.0 torchvision>=0.15.0

# Install other requirements
pip install -r requirements.txt
```

## 🚀 Usage

### Start the Application
```bash
streamlit run ocr_engine_streamlit.py
```

### Step-by-Step Workflow

1. **Choose OCR Model**
   - Click on EasyOCR (recommended for GPU), DocTR, or PaddleOCR
   - GPU capability notes are displayed for each model

2. **Upload PDF**
   - Use the file uploader to select your PDF
   - PDF will be loaded and page count displayed

3. **Select Pages**
   - **Quick Options**: All Pages, First Page, First 3 Pages
   - **Individual Selection**: Check boxes for specific pages (≤10 pages)
   - **Bulk Selection**: Multi-select dropdown for large PDFs (>10 pages)
   - **Preview**: Thumbnail previews of selected pages

4. **Process Document**
   - Click the blue "Process X page(s) with [Model]" button
   - Real-time progress and timing displayed
   - Results appear with bounding boxes and confidence scores

5. **Review & Export**
   - View processing summary with performance metrics
   - Download JSON results with model and timing data

## 📊 Output Format

The JSON output includes enhanced metadata:

```json
{
  "document": "sample.pdf",
  "model_used": "EasyOCR",
  "pages": [
    {
      "page": 1,
      "processing_time_seconds": 1.23,
      "model_used": "EasyOCR",
      "blocks": [
        {
          "text": "Sample text",
          "bounding_box": [[x1, y1], [x2, y2], [x3, y3], [x4, y4]],
          "confidence": 0.98
        }
      ]
    }
  ],
  "summary": {
    "total_pages": 1,
    "total_text_blocks": 15,
    "total_processing_time_seconds": 1.23,
    "average_time_per_page": 1.23,
    "model_used": "EasyOCR",
    "gpu_acceleration": true,
    "device_used": "mps"
  }
}
```

## 🎯 Model Performance Comparison

| Model | GPU Support | Speed (GPU) | Speed (CPU) | Accuracy | Memory | Best For |
|-------|-------------|-------------|-------------|----------|---------|----------|
| **EasyOCR** | ✅ MPS | 3-5x faster | Good | Excellent | Moderate | General OCR |
| **EasyOCR + LayoutLMv3** | ✅ MPS | 2-4x faster | Good | Excellent+ | High | Structured docs |
| **Donut** | ✅ MPS | 1-3x faster | Good | Good | High | Document understanding |

### Expected Processing Times (per page)
- **EasyOCR + GPU**: 0.5-2s per page
- **EasyOCR + LayoutLMv3 + GPU**: 1-3s per page  
- **Donut + GPU**: 2-4s per page

## 🔧 Troubleshooting

### GPU Not Detected
```bash
python -c "import torch; print(torch.backends.mps.is_available())"
```
- Should return `True` for GPU support
- If `False`, check macOS version and hardware

### Model Installation Issues
```bash
# For EasyOCR issues
pip uninstall easyocr
pip install easyocr

# For EasyOCR + LayoutLMv3 issues  
pip uninstall transformers
pip install transformers>=4.30.0

# For Donut issues
pip uninstall donut-python
pip install donut-python transformers>=4.30.0
```

### Memory Issues
- Reduce PDF resolution: `dpi=300` → `dpi=200`
- Process fewer pages at once
- Use EasyOCR (lower memory) instead of LayoutLMv3 or Donut

## 🧪 Testing GPU Performance

```python
import torch
import time

# Test MPS availability
print(f"MPS Available: {torch.backends.mps.is_available()}")
print(f"MPS Built: {torch.backends.mps.is_built()}")

# Simple performance test
device = "mps" if torch.backends.mps.is_available() else "cpu"
x = torch.randn(1000, 1000).to(device)
start = time.time()
y = torch.matmul(x, x)
print(f"Matrix multiplication on {device}: {time.time() - start:.4f}s")
```

## 📈 Expected Performance Gains

- **Small PDFs** (1-5 pages): 2-3x speedup
- **Medium PDFs** (5-20 pages): 3-4x speedup  
- **Large PDFs** (20+ pages): 4-5x speedup

## 🔮 Future Enhancements

- [ ] Batch processing for multiple PDFs
- [ ] Custom model fine-tuning
- [ ] OCR accuracy optimization
- [ ] Multi-language support enhancement
- [ ] Cloud deployment options

## 📝 Dependencies

- `torch>=2.0.0`: PyTorch with Metal support
- `torchvision>=0.15.0`: Computer vision utilities
- `easyocr>=1.7.0`: GPU-compatible OCR engine
- `transformers>=4.30.0`: Hugging Face transformers for LayoutLMv3 and Donut
- `donut-python>=1.0.9`: Donut document understanding model
- `streamlit>=1.20.0`: Web interface
- `pdf2image>=1.16.0`: PDF to image conversion
- `pillow>=9.0.0`: Image processing
- `numpy>=1.21.0`: Numerical computing
- `opencv-python>=4.6.0`: Computer vision

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📄 License

This project maintains the same license as the original codebase.