import streamlit as st
import requests
import json
import time
import os
from typing import Dict, List, Any, Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
from loguru import logger

# Configure page
st.set_page_config(
    page_title="Insurance Submission Extraction Engine",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configure logging
logger.add("logs/webapp.log", rotation="10 MB")
os.makedirs("logs", exist_ok=True)

# Service URLs from environment variables
SERVICES = {
    "pdf_renderer": os.getenv("PDF_RENDERER_URL", "http://pdf-renderer:8000"),
    "paddleocr": os.getenv("PADDLEOCR_URL", "http://paddleocr:8000"),
    "template_matcher": os.getenv("TEMPLATE_MATCHER_URL", "http://template-matcher:8000"),
    "rule_parser": os.getenv("RULE_PARSER_URL", "http://rule-parser:8000"),
    "layoutlm": os.getenv("LAYOUTLM_URL", "http://layoutlm:8000"),
    "normalizer": os.getenv("NORMALIZER_URL", "http://normalizer:8000"),
    "storage": os.getenv("STORAGE_URL", "http://storage:8000"),
    "logger": os.getenv("LOGGER_URL", "http://logger:8000"),
}

# Initialize session state
if "processing_results" not in st.session_state:
    st.session_state.processing_results = {}
if "current_job_id" not in st.session_state:
    st.session_state.current_job_id = None


def check_services_health():
    """Check health status of all services"""
    health_status = {}
    
    for service_name, service_url in SERVICES.items():
        try:
            response = requests.get(f"{service_url}/health", timeout=5)
            if response.status_code == 200:
                health_status[service_name] = {"status": "healthy", "details": response.json()}
            else:
                health_status[service_name] = {"status": "unhealthy", "details": {"error": f"HTTP {response.status_code}"}}
        except Exception as e:
            health_status[service_name] = {"status": "error", "details": {"error": str(e)}}
    
    return health_status


def render_pdf(uploaded_file) -> Optional[Dict[str, Any]]:
    """Render PDF to images"""
    try:
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
        response = requests.post(f"{SERVICES['pdf_renderer']}/render", files=files, timeout=60)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"PDF rendering failed: {response.text}")
            return None
            
    except Exception as e:
        st.error(f"Error rendering PDF: {str(e)}")
        return None


def extract_ocr(render_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Extract text using OCR"""
    try:
        ocr_request = {
            "job_id": render_result["job_id"],
            "image_paths": render_result["images"]
        }
        
        response = requests.post(
            f"{SERVICES['paddleocr']}/extract", 
            json=ocr_request, 
            timeout=120
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"OCR extraction failed: {response.text}")
            return None
            
    except Exception as e:
        st.error(f"Error during OCR extraction: {str(e)}")
        return None


def match_template(ocr_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Match document against templates"""
    try:
        match_request = {
            "job_id": ocr_result["job_id"],
            "tokens": ocr_result["tokens"],
            "page_count": ocr_result["page_count"]
        }
        
        response = requests.post(
            f"{SERVICES['template_matcher']}/match", 
            json=match_request, 
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Template matching failed: {response.text}")
            return None
            
    except Exception as e:
        st.error(f"Error during template matching: {str(e)}")
        return None


def parse_with_rules(ocr_result: Dict[str, Any], template_match: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Parse fields using rule-based extraction"""
    try:
        if not template_match["best_match"]:
            st.warning("No template match found, skipping rule-based parsing")
            return None
            
        parse_request = {
            "job_id": ocr_result["job_id"],
            "tokens": ocr_result["tokens"],
            "template_match": template_match["best_match"],
            "page_count": ocr_result["page_count"]
        }
        
        response = requests.post(
            f"{SERVICES['rule_parser']}/parse", 
            json=parse_request, 
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Rule-based parsing failed: {response.text}")
            return None
            
    except Exception as e:
        st.error(f"Error during rule-based parsing: {str(e)}")
        return None


def display_confidence_heatmap(tokens: List[Dict[str, Any]]):
    """Display confidence heatmap of OCR tokens"""
    if not tokens:
        return
    
    # Prepare data for heatmap
    confidences = [token["confidence"] for token in tokens]
    pages = [token["page"] for token in tokens]
    
    # Group by page
    page_confidences = {}
    for token in tokens:
        page = token["page"]
        if page not in page_confidences:
            page_confidences[page] = []
        page_confidences[page].append(token["confidence"])
    
    # Calculate average confidence per page
    avg_confidences = {page: sum(confs)/len(confs) for page, confs in page_confidences.items()}
    
    # Create bar chart
    fig = px.bar(
        x=list(avg_confidences.keys()),
        y=list(avg_confidences.values()),
        title="Average OCR Confidence by Page",
        labels={"x": "Page", "y": "Average Confidence"},
        color=list(avg_confidences.values()),
        color_continuous_scale="RdYlGn"
    )
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)


def display_extracted_fields(fields: List[Dict[str, Any]]):
    """Display extracted fields in an editable format"""
    if not fields:
        st.info("No fields extracted")
        return
    
    st.subheader("📋 Extracted Fields")
    
    # Convert to DataFrame for display
    field_data = []
    for field in fields:
        field_data.append({
            "Field Name": field["field_name"],
            "Value": str(field["value"]),
            "Confidence": f"{field['confidence']:.3f}",
            "Confidence Level": field["confidence_level"],
            "Extraction Method": field["extraction_method"],
            "Source Tokens": len(field["source_tokens"])
        })
    
    df = pd.DataFrame(field_data)
    
    # Display as editable dataframe
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "Field Name": st.column_config.TextColumn("Field Name", width="medium"),
            "Value": st.column_config.TextColumn("Value", width="large"),
            "Confidence": st.column_config.NumberColumn("Confidence", format="%.3f"),
            "Confidence Level": st.column_config.SelectboxColumn(
                "Confidence Level",
                options=["high", "medium", "low"]
            ),
        }
    )
    
    return edited_df


def display_processing_metrics(results: Dict[str, Any]):
    """Display processing metrics"""
    st.subheader("⏱️ Processing Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        pdf_time = results.get("render_result", {}).get("processing_time", 0)
        st.metric("PDF Rendering", f"{pdf_time:.2f}s")
    
    with col2:
        ocr_time = results.get("ocr_result", {}).get("processing_time", 0)
        st.metric("OCR Processing", f"{ocr_time:.2f}s")
    
    with col3:
        template_time = results.get("template_match", {}).get("processing_time", 0)
        st.metric("Template Matching", f"{template_time:.2f}s")
    
    with col4:
        parse_time = results.get("parsing_result", {}).get("processing_time", 0)
        st.metric("Field Extraction", f"{parse_time:.2f}s")
    
    # Total processing time
    total_time = pdf_time + ocr_time + template_time + parse_time
    st.metric("Total Processing Time", f"{total_time:.2f}s")
    
    # OCR statistics
    if "ocr_result" in results:
        tokens = results["ocr_result"].get("tokens", [])
        if tokens:
            avg_confidence = sum(t["confidence"] for t in tokens) / len(tokens)
            st.metric("Average OCR Confidence", f"{avg_confidence:.3f}")
            st.metric("Total OCR Tokens", len(tokens))


def export_results(results: Dict[str, Any], format_type: str = "json"):
    """Export results in specified format"""
    if format_type == "json":
        return json.dumps(results, indent=2, default=str)
    elif format_type == "csv":
        if "parsing_result" in results and "extracted_fields" in results["parsing_result"]:
            fields = results["parsing_result"]["extracted_fields"]
            df = pd.DataFrame([
                {
                    "field_name": f["field_name"],
                    "value": str(f["value"]),
                    "confidence": f["confidence"],
                    "confidence_level": f["confidence_level"],
                    "extraction_method": f["extraction_method"]
                }
                for f in fields
            ])
            return df.to_csv(index=False)
    return ""


def main():
    """Main Streamlit application"""
    
    # Header
    st.title("📄 Insurance Submission Extraction Engine")
    st.markdown("Upload insurance documents and extract structured data using OCR and AI-powered field extraction.")
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 System Status")
        
        if st.button("Check Services Health"):
            with st.spinner("Checking services..."):
                health_status = check_services_health()
                
                for service, status in health_status.items():
                    if status["status"] == "healthy":
                        st.success(f"✅ {service}")
                    elif status["status"] == "unhealthy":
                        st.warning(f"⚠️ {service}")
                    else:
                        st.error(f"❌ {service}")
        
        st.divider()
        
        # Processing options
        st.header("⚙️ Processing Options")
        use_layoutlm = st.checkbox("Use LayoutLM for unknown layouts", value=False, disabled=True)
        confidence_threshold = st.slider("Confidence Threshold", 0.0, 1.0, 0.75)
        
        st.divider()
        
        # Export options
        st.header("📤 Export Options")
        export_format = st.selectbox("Export Format", ["JSON", "CSV"])
    
    # Main content
    tab1, tab2, tab3 = st.tabs(["📤 Upload & Process", "📊 Results", "🔍 Analysis"])
    
    with tab1:
        st.header("Upload Insurance Document")
        
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=["pdf"],
            help="Upload an insurance submission document in PDF format"
        )
        
        if uploaded_file is not None:
            st.success(f"File uploaded: {uploaded_file.name}")
            
            if st.button("🚀 Process Document", type="primary"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Step 1: Render PDF
                status_text.text("Step 1/4: Rendering PDF to images...")
                progress_bar.progress(25)
                
                render_result = render_pdf(uploaded_file)
                if not render_result:
                    st.stop()
                
                # Step 2: OCR Extraction
                status_text.text("Step 2/4: Extracting text with OCR...")
                progress_bar.progress(50)
                
                ocr_result = extract_ocr(render_result)
                if not ocr_result:
                    st.stop()
                
                # Step 3: Template Matching
                status_text.text("Step 3/4: Matching document template...")
                progress_bar.progress(75)
                
                template_match = match_template(ocr_result)
                if not template_match:
                    st.stop()
                
                # Step 4: Field Extraction
                status_text.text("Step 4/4: Extracting fields...")
                progress_bar.progress(90)
                
                parsing_result = parse_with_rules(ocr_result, template_match)
                
                # Complete
                progress_bar.progress(100)
                status_text.text("✅ Processing completed!")
                
                # Store results
                results = {
                    "filename": uploaded_file.name,
                    "render_result": render_result,
                    "ocr_result": ocr_result,
                    "template_match": template_match,
                    "parsing_result": parsing_result,
                    "processed_at": time.time()
                }
                
                st.session_state.processing_results = results
                st.session_state.current_job_id = render_result["job_id"]
                
                st.success("🎉 Document processed successfully!")
                st.rerun()
    
    with tab2:
        if st.session_state.processing_results:
            results = st.session_state.processing_results
            
            # Template matching results
            st.header("🎯 Template Matching")
            template_match = results.get("template_match", {})
            
            if template_match.get("best_match"):
                match = template_match["best_match"]
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Matched Template", match["template_id"])
                    st.metric("Match Confidence", f"{match['confidence']:.3f}")
                
                with col2:
                    st.write("**Matched Keywords:**")
                    for keyword in match["matched_keywords"]:
                        st.badge(keyword)
            else:
                st.warning("No template match found")
            
            st.divider()
            
            # Extracted fields
            parsing_result = results.get("parsing_result")
            if parsing_result and "extracted_fields" in parsing_result:
                edited_fields = display_extracted_fields(parsing_result["extracted_fields"])
            
            st.divider()
            
            # Processing metrics
            display_processing_metrics(results)
            
            st.divider()
            
            # Export section
            st.header("📤 Export Results")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Download JSON"):
                    json_data = export_results(results, "json")
                    st.download_button(
                        label="Download JSON File",
                        data=json_data,
                        file_name=f"extraction_results_{results['filename']}.json",
                        mime="application/json"
                    )
            
            with col2:
                if st.button("Download CSV"):
                    csv_data = export_results(results, "csv")
                    if csv_data:
                        st.download_button(
                            label="Download CSV File",
                            data=csv_data,
                            file_name=f"extraction_results_{results['filename']}.csv",
                            mime="text/csv"
                        )
        else:
            st.info("👆 Upload and process a document first to see results here.")
    
    with tab3:
        if st.session_state.processing_results:
            results = st.session_state.processing_results
            
            # OCR confidence analysis
            st.header("🔍 OCR Confidence Analysis")
            ocr_result = results.get("ocr_result", {})
            if "tokens" in ocr_result:
                display_confidence_heatmap(ocr_result["tokens"])
            
            st.divider()
            
            # Template matching details
            st.header("🎯 Template Matching Details")
            template_match = results.get("template_match", {})
            
            if "all_matches" in template_match:
                match_data = []
                for match in template_match["all_matches"]:
                    match_data.append({
                        "Template": match["template_id"],
                        "Confidence": match["confidence"],
                        "Is Match": match["is_match"],
                        "Keywords Matched": len(match["matched_keywords"])
                    })
                
                df_matches = pd.DataFrame(match_data)
                st.dataframe(df_matches, use_container_width=True)
            
            st.divider()
            
            # Raw OCR tokens (for debugging)
            with st.expander("🔍 Raw OCR Tokens"):
                if "tokens" in ocr_result:
                    tokens_df = pd.DataFrame([
                        {
                            "Text": token["text"],
                            "Confidence": token["confidence"],
                            "Page": token["page"],
                            "X1": token["bbox"]["x1"],
                            "Y1": token["bbox"]["y1"],
                            "X2": token["bbox"]["x2"],
                            "Y2": token["bbox"]["y2"]
                        }
                        for token in ocr_result["tokens"]
                    ])
                    st.dataframe(tokens_df, use_container_width=True)
        else:
            st.info("👆 Upload and process a document first to see analysis here.")


if __name__ == "__main__":
    main()