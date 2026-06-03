import os
import sys
import subprocess
from pathlib import Path

# Ensure dependencies are installed
try:
    import fitz  # PyMuPDF
except ImportError:
    print("Installing PyMuPDF for visualization...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pymupdf"])
    import fitz

from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import PdfFormatOption

ROOT_DIR = Path(__file__).parent.parent.parent
INPUTS_DIR = ROOT_DIR / "test" / "inputs"
OUTPUTS_DIR = ROOT_DIR / "test" / "outputs"

def draw_layout():
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    
    # We will just test with the first PDF
    pdf_files = list(INPUTS_DIR.glob("*.pdf"))
    if not pdf_files:
        print("No PDFs found in test/inputs/")
        return
        
    target_pdf = pdf_files[0]
    print(f"Visualizing layout for {target_pdf.name}...")

    # Configure Docling
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = True
    pipeline_options.do_table_structure = True

    converter = DocumentConverter(
        allowed_formats=[InputFormat.PDF],
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    print("Running Docling extraction...")
    result = converter.convert(target_pdf)
    doc = result.document

    # Open PDF with PyMuPDF to draw
    pdf_doc = fitz.open(target_pdf)
    
    # Process each page
    for page_num in range(len(pdf_doc)):
        page = pdf_doc[page_num]
        page_height = page.rect.height
        
        # Docling pages are 1-indexed
        docling_page_no = page_num + 1
        
        # Gather all elements on this page
        elements_on_page = []
        for el in doc.texts:
            if hasattr(el, "prov") and el.prov:
                prov = el.prov[0] if isinstance(el.prov, list) else el.prov
                if hasattr(prov, "page_no") and prov.page_no == docling_page_no:
                    elements_on_page.append(el)
                    
        print(f"Found {len(elements_on_page)} text elements on page {docling_page_no}")
        
        # Draw bounding boxes
        for el in elements_on_page:
            prov = el.prov[0] if isinstance(el.prov, list) else el.prov
            if not hasattr(prov, "bbox"):
                continue
                
            bbox = prov.bbox
            
            # Determine color based on label
            label = str(getattr(el, "label", "")).lower()
            if "title" in label or "heading" in label:
                color = (1, 0, 0) # Red for headings
                width = 2
            elif "section" in label:
                color = (1, 0.5, 0) # Orange for subheadings
                width = 1.5
            elif "list" in label:
                color = (0, 0.5, 0) # Green for lists
                width = 1
            else:
                color = (0, 0, 1) # Blue for normal text
                width = 1
                
            # Parse bbox
            # Docling BBox is bottom-left origin
            l = getattr(bbox, "l", getattr(bbox, "x", getattr(bbox, "x0", 0)))
            r = getattr(bbox, "r", getattr(bbox, "x1", l))
            t = getattr(bbox, "t", getattr(bbox, "y", getattr(bbox, "y1", 0)))
            b = getattr(bbox, "b", getattr(bbox, "y0", 0))
            
            if r == l and hasattr(bbox, "width"): r = l + bbox.width
            if b == t and hasattr(bbox, "height"): b = t - bbox.height
            
            # Convert to PyMuPDF top-left origin coordinates
            # FitZ rect: x0, y0, x1, y1 (top-left, bottom-right)
            y0 = page_height - t
            y1 = page_height - b
            
            rect = fitz.Rect(l, y0, r, y1)
            
            # Draw rectangle with semi-transparent fill
            page.draw_rect(rect, color=color, fill=color, fill_opacity=0.25, width=width)
            
            # Optional: Add small label text
            page.insert_text(fitz.Point(l, y0 - 2), label, fontsize=6, color=color)

        # Save page as image
        pix = page.get_pixmap(dpi=150)
        out_path = OUTPUTS_DIR / f"{target_pdf.stem}_layout_page{docling_page_no}.png"
        pix.save(str(out_path))
        print(f"Saved visualization to {out_path.name}")
        
    pdf_doc.close()
    print("Done!")

if __name__ == "__main__":
    draw_layout()
