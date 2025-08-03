import streamlit as st
from pdf2image import convert_from_path
from PIL import Image, ImageDraw
import numpy as np
import json
import tempfile
import os
import time

# Initialize OCR engines (lazy loading)
ocr_engines = {}

def check_gpu_availability():
    """Check if Mac GPU (MPS) is available for PyTorch models"""
    try:
        import torch
        if torch.backends.mps.is_available():
            return True, "mps"
        elif torch.cuda.is_available():
            return True, "cuda"
        else:
            return False, "cpu"
    except ImportError:
        return False, "cpu"

def get_model_info():
    """Get information about available OCR models and their GPU support"""
    gpu_available, device = check_gpu_availability()
    
    models = {
        "EasyOCR": {
            "gpu_support": True,
            "description": "PyTorch-based, excellent text recognition",
            "gpu_note": "✅ Full GPU acceleration" if gpu_available else "❌ GPU not available",
            "recommended": True
        },
        "EasyOCR + LayoutLMv3": {
            "gpu_support": True,
            "description": "OCR + FUNSD Fine-tuned Document Understanding (Forms, Headers, Q&A)",
            "gpu_note": "✅ Full GPU acceleration" if gpu_available else "❌ GPU not available",
            "recommended": gpu_available
        },
        "Donut": {
            "gpu_support": True,
            "description": "OCR-free Document Understanding, transformer-based",
            "gpu_note": "✅ Full GPU acceleration" if gpu_available else "❌ GPU not available",
            "recommended": False
        }
    }
    
    return models

@st.cache_resource
def get_ocr_engine(model_name):
    """Initialize OCR engine based on selected model"""
    global ocr_engines
    
    if model_name not in ocr_engines:
        gpu_available, device = check_gpu_availability()
        device_str = device if gpu_available else "cpu"
        
        with st.spinner(f"🔄 Loading {model_name} (first time only)..."):
            if model_name == "EasyOCR":
                try:
                    import easyocr
                    use_gpu = gpu_available
                    ocr_engines[model_name] = easyocr.Reader(['en'], gpu=use_gpu)
                except ImportError:
                    st.error("EasyOCR not installed. Please install with: pip install easyocr")
                    return None
                
            elif model_name == "EasyOCR + LayoutLMv3":
                try:
                    import easyocr
                    from transformers import LayoutLMv3Processor, LayoutLMv3ForTokenClassification
                    import torch
                    
                    # Load EasyOCR for text extraction
                    easy_ocr = easyocr.Reader(['en'], gpu=gpu_available)
                    
                    # Load LayoutLMv3 for document understanding (disable built-in OCR)
                    # Using FUNSD fine-tuned model for better form/document understanding
                    # FUNSD = Form Understanding in Noisy Scanned Documents
                    # This model is specifically trained to identify: HEADER, QUESTION, ANSWER, OTHER
                    processor = LayoutLMv3Processor.from_pretrained("nielsr/layoutlmv3-finetuned-funsd", apply_ocr=False)
                    model = LayoutLMv3ForTokenClassification.from_pretrained("nielsr/layoutlmv3-finetuned-funsd")
                    
                    if gpu_available:
                        model = model.to(device_str)
                    
                    ocr_engines[model_name] = {
                        "easyocr": easy_ocr,
                        "processor": processor,
                        "model": model,
                        "device": device_str
                    }
                except ImportError as e:
                    st.error(f"Dependencies not installed: {e}")
                    st.info("Please install with: pip install easyocr transformers")
                    return None
                    
            elif model_name == "Donut":
                try:
                    from transformers import DonutProcessor, VisionEncoderDecoderModel
                    import torch
                    
                    # Load Donut model for OCR-free document understanding
                    processor = DonutProcessor.from_pretrained("naver-clova-ix/donut-base-finetuned-docvqa")
                    model = VisionEncoderDecoderModel.from_pretrained("naver-clova-ix/donut-base-finetuned-docvqa")
                    
                    if gpu_available:
                        model = model.to(device_str)
                    
                    ocr_engines[model_name] = {
                        "processor": processor,
                        "model": model,
                        "device": device_str
                    }
                except ImportError as e:
                    st.error(f"Dependencies not installed: {e}")
                    st.info("Please install with: pip install transformers")
                    return None
    
    return ocr_engines.get(model_name)

def normalize_box(box, width, height):
    """
    Convert pixel coords (x0,y0,x1,y1) to LayoutLMv3 0-1000 space.
    
    LayoutLMv3 expects bounding boxes to be normalized to a 0-1000 coordinate system
    regardless of the original image size. This normalization is crucial for proper
    document understanding and entity recognition.
    """
    x0, y0, x1, y1 = box
    return [
        int(1000 * x0 / width),
        int(1000 * y0 / height),
        int(1000 * x1 / width),
        int(1000 * y1 / height)
    ]

# Spatial clustering function to group nearby elements
def spatial_cluster(elements, distance_threshold=100):
    """
    Group elements that are spatially close to each other.
    Uses simple distance-based clustering.
    """
    if not elements:
        return []
    
    clusters = []
    used = set()
    
    for i, element in enumerate(elements):
        if i in used:
            continue
            
        # Start a new cluster with this element
        cluster = [element]
        used.add(i)
        
        # Find all other elements within distance threshold
        for j, other_element in enumerate(elements):
            if j in used:
                continue
                
            # Calculate distance between centers
            dx = element["center"][0] - other_element["center"][0]
            dy = element["center"][1] - other_element["center"][1]
            distance = (dx**2 + dy**2)**0.5
            
            if distance <= distance_threshold:
                cluster.append(other_element)
                used.add(j)
        
        clusters.append(cluster)
    
    return clusters

# Convert PDF file to image list
def convert_pdf_to_images(pdf_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(pdf_file.read())
        tmp_file_path = tmp_file.name
    images = convert_from_path(tmp_file_path, dpi=300)
    os.unlink(tmp_file_path)
    return images

# Extract OCR results with bounding boxes
def extract_text_and_boxes(image, model_name):
    ocr_engine = get_ocr_engine(model_name)
    if ocr_engine is None:
        return []
    
    image_np = np.array(image)
    blocks = []

    if model_name == "EasyOCR":
        result = ocr_engine.readtext(image_np)
        for detection in result:
            box, text, conf = detection
            if text.strip():
                # Convert EasyOCR box format
                formatted_box = [[float(point[0]), float(point[1])] for point in box]
                blocks.append({
                    "text": text,
                    "bounding_box": formatted_box,
                    "confidence": round(conf, 4)
                })
    
    elif model_name == "EasyOCR + LayoutLMv3":
        try:
            import torch
            easy_ocr = ocr_engine["easyocr"]
            processor = ocr_engine["processor"]
            model = ocr_engine["model"]
            device_str = ocr_engine["device"]
            
            # Step 1: Use EasyOCR for text extraction
            ocr_result = easy_ocr.readtext(image_np)
            
            if not ocr_result:
                return blocks
            
            # Step 2: Prepare data for LayoutLMv3
            words = []
            boxes = []
            
            # Get image dimensions for normalization
            width, height = image.size
            
            for detection in ocr_result:
                box, text, conf = detection
                if text.strip():
                    words.append(text)
                    # Convert EasyOCR box format to LayoutLMv3 format (x0, y0, x1, y1)
                    x_coords = [point[0] for point in box]
                    y_coords = [point[1] for point in box]
                    x0, x1 = min(x_coords), max(x_coords)
                    y0, y1 = min(y_coords), max(y_coords)
                    
                    # Normalize bounding box to 0-1000 coordinate space for LayoutLMv3
                    normalized_box = normalize_box([x0, y0, x1, y1], width, height)
                    boxes.append(normalized_box)
            
            # Step 3: Process with LayoutLMv3
            encoding = processor(image, words, boxes=boxes, return_tensors="pt", padding=True, truncation=True)
            if device_str != "cpu":
                encoding = {k: v.to(device_str) for k, v in encoding.items()}
            
            with torch.no_grad():
                outputs = model(**encoding)
                predictions = outputs.logits.argmax(-1).squeeze().tolist()
            
            # Step 4: Group tokens by entity labels and spatial proximity
            # FUNSD entity labels mapping
            funsd_labels = {
                0: "OTHER",
                1: "HEADER", 
                2: "QUESTION",
                3: "ANSWER"
            }
            
            # First, collect all elements by entity type
            entity_elements = {}
            for i, (detection, pred_label) in enumerate(zip(ocr_result, predictions if isinstance(predictions, list) else [predictions])):
                box, text, conf = detection
                if text.strip():
                    # Convert box format
                    formatted_box = [[float(point[0]), float(point[1])] for point in box]
                    
                    # Get meaningful FUNSD entity label
                    entity_label = funsd_labels.get(pred_label, f"UNKNOWN_{pred_label}")
                    
                    if entity_label not in entity_elements:
                        entity_elements[entity_label] = []
                    
                    # Calculate center point for spatial clustering
                    center_x = sum(point[0] for point in formatted_box) / len(formatted_box)
                    center_y = sum(point[1] for point in formatted_box) / len(formatted_box)
                    
                    entity_elements[entity_label].append({
                        "text": text,
                        "box": formatted_box,
                        "confidence": conf,
                        "center": (center_x, center_y)
                    })
            
            # Step 5: Spatially cluster elements within each entity type
            for entity_label, elements in entity_elements.items():
                clusters = spatial_cluster(elements, distance_threshold=100)  # 100 pixel threshold
                
                for cluster_idx, cluster in enumerate(clusters, 1):
                    # Combine text from all elements in this cluster
                    combined_text = " ".join([elem["text"] for elem in cluster])
                    
                    # Calculate average confidence
                    avg_confidence = sum(elem["confidence"] for elem in cluster) / len(cluster)
                    
                    # Calculate merged bounding box
                    all_x_coords = []
                    all_y_coords = []
                    individual_boxes = []
                    individual_confidences = []
                    individual_texts = []
                    
                    for elem in cluster:
                        individual_boxes.append(elem["box"])
                        individual_confidences.append(elem["confidence"])
                        individual_texts.append(elem["text"])
                        for point in elem["box"]:
                            all_x_coords.append(point[0])
                            all_y_coords.append(point[1])
                    
                    # Create merged bounding box
                    min_x, max_x = min(all_x_coords), max(all_x_coords)
                    min_y, max_y = min(all_y_coords), max(all_y_coords)
                    
                    merged_bounding_box = [
                        [min_x, min_y],  # top-left
                        [max_x, min_y],  # top-right
                        [max_x, max_y],  # bottom-right
                        [min_x, max_y]   # bottom-left
                    ]
                    
                    # Create group label (e.g., "header1", "question2", etc.)
                    group_label = f"{entity_label.lower()}{cluster_idx}" if len(clusters) > 1 else entity_label.lower()
                    
                    # Add clustered block
                    blocks.append({
                        "entity_label": entity_label,
                        "group_label": group_label,
                        "combined_text": combined_text,
                        "individual_texts": individual_texts,
                        "individual_boxes": individual_boxes,
                        "merged_bounding_box": merged_bounding_box,
                        "individual_confidences": [round(c, 4) for c in individual_confidences],
                        "average_confidence": round(avg_confidence, 4),
                        "token_count": len(cluster),
                        "enhanced": True,
                        "grouped_by_entity": True
                    })
                    
        except Exception as e:
            st.error(f"EasyOCR + LayoutLMv3 processing error: {e}")
            st.info("💡 Falling back to basic EasyOCR processing...")
            # Fallback to basic EasyOCR
            easy_ocr = ocr_engine["easyocr"]
            result = easy_ocr.readtext(image_np)
            for detection in result:
                box, text, conf = detection
                if text.strip():
                    formatted_box = [[float(point[0]), float(point[1])] for point in box]
                    blocks.append({
                        "text": text,
                        "bounding_box": formatted_box,
                        "confidence": round(conf, 4)
                    })
    
    elif model_name == "Donut":
        try:
            import torch
            processor = ocr_engine["processor"]
            model = ocr_engine["model"]
            device_str = ocr_engine["device"]
            
            # Process image with Donut
            pixel_values = processor(image, return_tensors="pt").pixel_values
            if device_str != "cpu":
                pixel_values = pixel_values.to(device_str)
            
            # Generate text using Donut (OCR-free approach)
            task_prompt = "<s_docvqa><s_question>What is the text in this document?</s_question><s_answer>"
            decoder_input_ids = processor.tokenizer(task_prompt, add_special_tokens=False, return_tensors="pt").input_ids
            if device_str != "cpu":
                decoder_input_ids = decoder_input_ids.to(device_str)
            
            outputs = model.generate(
                pixel_values,
                decoder_input_ids=decoder_input_ids,
                max_length=model.decoder.config.max_position_embeddings,
                pad_token_id=processor.tokenizer.pad_token_id,
                eos_token_id=processor.tokenizer.eos_token_id,
                use_cache=True,
                bad_words_ids=[[processor.tokenizer.unk_token_id]],
                return_dict_in_generate=True,
            )
            
            sequence = processor.batch_decode(outputs.sequences)[0]
            sequence = sequence.replace(processor.tokenizer.eos_token, "").replace(processor.tokenizer.pad_token, "")
            
            # Extract answer from the sequence
            answer_start = sequence.find("<s_answer>")
            if answer_start != -1:
                answer = sequence[answer_start + len("<s_answer>"):].strip()
                # Donut doesn't provide bounding boxes - only text output
                blocks.append({
                    "text": answer,
                    "bounding_box": None,  # No bounding boxes available
                    "confidence": 0.95,  # Donut doesn't provide confidence scores
                    "model_type": "transformer",
                    "no_bbox": True  # Flag to indicate no bounding box visualization
                })
                
        except Exception as e:
            st.error(f"Donut processing error: {e}")
            st.info("💡 Donut requires specific model configuration. Try EasyOCR as alternative.")
    
    return blocks

# Draw bounding boxes on top of the image
def draw_boxes_on_image(image, blocks):
    image_draw = image.convert("RGB")
    draw = ImageDraw.Draw(image_draw)

    for block in blocks:
        # Skip blocks without bounding boxes (e.g., Donut)
        if block.get("no_bbox", False):
            continue
        
        # Handle LayoutLMv3 spatially clustered entities
        if block.get("grouped_by_entity", False):
            entity_label = block["entity_label"]
            group_label = block["group_label"]
            avg_confidence = block["average_confidence"]
            combined_text = block["combined_text"]
            merged_box = block["merged_bounding_box"]
            token_count = block["token_count"]
            
            # RAG color coding based on average confidence of the spatial cluster
            color = "green" if avg_confidence > 0.9 else "orange" if avg_confidence > 0.5 else "red"
            
            # Draw the merged bounding box for this spatial cluster
            box_points = [tuple(point) for point in merged_box]
            
            # Draw merged bounding box with thicker line
            draw.line(box_points + [box_points[0]], fill=color, width=3)
            
            # Draw text with cluster info
            confidence_text = f'{combined_text[:50]}{"..." if len(combined_text) > 50 else ""} (avg: {avg_confidence:.2f}, items: {token_count}) [{group_label}]'
            try:
                draw.text(box_points[0], confidence_text, fill=color)
            except:
                draw.text(box_points[0], f'{group_label}', fill=color)
        
        # Handle regular EasyOCR blocks
        elif "bounding_box" in block and block["bounding_box"] is not None:
            box = [tuple(point) for point in block["bounding_box"]]
            confidence = block["confidence"]
            text = block["text"]
            
            # Color by individual confidence
            color = "green" if confidence > 0.9 else "orange" if confidence > 0.5 else "red"
            confidence_text = f'{text} ({confidence:.2f})'
            
            # Draw bounding box
            draw.line(box + [box[0]], fill=color, width=2)
            
            # Draw text with confidence
            try:
                draw.text(box[0], confidence_text, fill=color)
            except:
                draw.text(box[0], text, fill=color)

    return image_draw

# Streamlit app
def run_app():
    st.set_page_config(layout="wide")
    st.title("📄 Multi-Engine OCR PDF Visualizer")
    
    # Display GPU information
    gpu_available, device = check_gpu_availability()
    if gpu_available:
        st.success(f"🚀 GPU Acceleration: {device.upper()} ready for faster processing!")
    else:
        st.info("💻 Running in CPU mode")
    
    st.markdown("---")
    
    # Model Selection
    st.subheader("🤖 Select OCR Model")
    models = get_model_info()
    
    # Create columns for model selection
    cols = st.columns(len(models))
    
    selected_model = None
    for i, (model_name, info) in enumerate(models.items()):
        with cols[i]:
            recommended_text = " (Recommended)" if info["recommended"] else ""
            if st.button(f"{model_name}{recommended_text}", key=f"model_{model_name}"):
                selected_model = model_name
                st.session_state.selected_model = model_name
            
            st.caption(f"**{info['description']}**")
            st.caption(f"GPU: {info['gpu_note']}")
    
    # Display selected model
    if 'selected_model' in st.session_state:
        selected_model = st.session_state.selected_model
        st.info(f"Selected Model: **{selected_model}**")
    
    st.markdown("---")

    uploaded_pdf = st.file_uploader("Upload a PDF file", type=["pdf"])

    if uploaded_pdf:
        # Convert PDF to images for preview
        with st.spinner("📖 Loading PDF pages..."):
            images = convert_pdf_to_images(uploaded_pdf)
        
        st.success(f"✅ PDF loaded: {len(images)} pages found")
        
        # Page Selection
        st.subheader("📑 Select Pages to Process")
        
        # Quick selection options
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("All Pages"):
                st.session_state.selected_pages = list(range(1, len(images) + 1))
        with col2:
            if st.button("First Page"):
                st.session_state.selected_pages = [1]
        with col3:
            if st.button("First 3 Pages"):
                st.session_state.selected_pages = list(range(1, min(4, len(images) + 1)))
        with col4:
            if st.button("Clear Selection"):
                st.session_state.selected_pages = []
        
        # Individual page selection
        if len(images) <= 10:
            # For small PDFs, show checkboxes
            st.write("**Select specific pages:**")
            page_cols = st.columns(min(5, len(images)))
            selected_pages = []
            
            for i in range(len(images)):
                with page_cols[i % 5]:
                    key = f"page_{i+1}"
                    default_value = (i+1) in st.session_state.get('selected_pages', [])
                    if st.checkbox(f"Page {i+1}", value=default_value, key=key):
                        selected_pages.append(i+1)
            
            if selected_pages:
                st.session_state.selected_pages = selected_pages
        else:
            # For large PDFs, use multiselect
            page_options = list(range(1, len(images) + 1))
            default_selection = st.session_state.get('selected_pages', [1])
            selected_pages = st.multiselect(
                "Select pages:", 
                page_options, 
                default=default_selection,
                help="Type page numbers or select from dropdown"
            )
            st.session_state.selected_pages = selected_pages
        
        # Display selected pages
        selected_pages = st.session_state.get('selected_pages', [])
        if selected_pages:
            st.info(f"📋 Selected pages: {', '.join(map(str, selected_pages))}")
            
            # Show preview thumbnails
            if len(selected_pages) <= 5:
                st.write("**Preview of selected pages:**")
                preview_cols = st.columns(len(selected_pages))
                for i, page_num in enumerate(selected_pages):
                    with preview_cols[i]:
                        st.image(images[page_num-1], caption=f"Page {page_num}", width=150)
        
        st.markdown("---")
        
        # Process Button
        if selected_pages and 'selected_model' in st.session_state:
            process_button = st.button(
                f"🚀 Process {len(selected_pages)} page(s) with {st.session_state.selected_model}",
                type="primary",
                help=f"This will process the selected pages using {st.session_state.selected_model}"
            )
            
            if process_button:
                # Processing logic
                start_time = time.time()
                selected_model = st.session_state.selected_model
                
                with st.spinner(f"🔍 Processing {len(selected_pages)} pages with {selected_model}..."):
                    document_output = {
                        "document": uploaded_pdf.name, 
                        "model_used": selected_model,
                        "pages": []
                    }
                    total_blocks = 0

                    for page_num in selected_pages:
                        page_start_time = time.time()
                        st.subheader(f"Page {page_num}")
                        
                        image = images[page_num-1]
                        blocks = extract_text_and_boxes(image, selected_model)
                        total_blocks += len(blocks)
                        boxed_image = draw_boxes_on_image(image, blocks)
                        
                        page_processing_time = time.time() - page_start_time

                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.image(boxed_image, use_column_width=True)
                        with col2:
                            st.metric("Text Blocks Found", len(blocks))
                            st.metric("Processing Time", f"{page_processing_time:.2f}s")
                            st.metric("Model Used", selected_model)

                        page_json = {
                            "page": page_num,
                            "blocks": blocks,
                            "processing_time_seconds": round(page_processing_time, 2),
                            "model_used": selected_model
                        }
                        document_output["pages"].append(page_json)

                        with st.expander("📦 JSON Output for this Page"):
                            st.json(page_json)

                    total_processing_time = time.time() - start_time
                    
                    # Add summary metrics
                    document_output["summary"] = {
                        "total_pages": len(selected_pages),
                        "total_text_blocks": total_blocks,
                        "total_processing_time_seconds": round(total_processing_time, 2),
                        "average_time_per_page": round(total_processing_time / len(selected_pages), 2),
                        "model_used": selected_model,
                        "gpu_acceleration": gpu_available,
                        "device_used": device if gpu_available else "cpu"
                    }
                    
                    # Display summary
                    st.markdown("---")
                    st.subheader("📊 Processing Summary")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Pages Processed", len(selected_pages))
                    with col2:
                        st.metric("Total Text Blocks", total_blocks)
                    with col3:
                        st.metric("Total Time", f"{total_processing_time:.2f}s")
                    with col4:
                        st.metric("Avg Time/Page", f"{total_processing_time/len(selected_pages):.2f}s")

                    st.download_button(
                        label="⬇️ Download JSON Results",
                        data=json.dumps(document_output, indent=2),
                        file_name=f"ocr_output_{selected_model.lower()}.json",
                        mime="application/json"
                    )
        
        elif not selected_pages:
            st.warning("⚠️ Please select at least one page to process")
        elif 'selected_model' not in st.session_state:
            st.warning("⚠️ Please select an OCR model first")

# Run the app
if __name__ == "__main__":
    run_app()