import os
import sys
import json
import base64
import asyncio
import re
from pathlib import Path
from dotenv import load_dotenv
import httpx

# Load environment variables
root_dir = Path(__file__).resolve().parent.parent.parent
env_path = root_dir / "server" / ".env"

if not env_path.exists():
    print(f"Error: Cannot find .env at {env_path}")
    sys.exit(1)

load_dotenv(env_path)

VLM_API_KEY = os.getenv("VLM_API_KEY")
VLM_MODEL = os.getenv("VLM_MODEL", "meta/llama-3.2-90b-vision-instruct")

if not VLM_API_KEY:
    print("Error: VLM_API_KEY is not set in server/.env")
    sys.exit(1)

INPUTS_DIR = root_dir / "shared" / "inputs"
OUTPUTS_DIR = root_dir / "server" / "templates"

INPUTS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)


PROMPT = """You are a master UI/UX designer and frontend engineer. 
Your task is to analyze this resume template image and extract EVERY INCH of visual layout specifications so it can be perfectly recreated using HTML/CSS in a resume builder.

You MUST extract and output a JSON object containing the exact properties listed below.
Do not output anything other than raw, valid JSON. No markdown fences. No explanations.

{
  "color_palette": {
    "primary": "#HEX (Main accent color used for headings, borders, or icons)",
    "secondary": "#HEX (Secondary color)",
    "background": "#HEX (Page background color, usually #FFFFFF)",
    "text": "#HEX (Main body text color, e.g., #1A1A1A)"
  },
  "typography": {
    "h1": {"font_family": "Closest web-safe font", "size_pt": "integer", "weight": "bold/normal", "text_transform": "uppercase/none"},
    "h2": {"font_family": "Closest web-safe font", "size_pt": "integer", "weight": "bold/normal", "text_transform": "uppercase/none"},
    "body": {"font_family": "Closest web-safe font", "size_pt": "integer", "weight": "bold/normal", "line_height": "float"}
  },
  "layout": {
    "columns": "integer (1, 2, or 3)",
    "column_ratio": "string (e.g., '100%' for 1 col, '30:70' for 2 col left sidebar, '70:30' for 2 col right sidebar)",
    "margins": {"top": "px/pt", "bottom": "px/pt", "left": "px/pt", "right": "px/pt"}
  },
  "sections_layout": {
    "main_column": ["List of sections in the main wider column, top-to-bottom"],
    "sidebar_column": ["List of sections in the sidebar column, top-to-bottom. Leave empty if 1 column layout"]
  },
  "visual_elements": {
    "dividers": {"present": true/false, "color": "#HEX", "thickness": "px"},
    "bullet_style": "round / dash / square / none",
    "icon_usage": "none / contact_only / section_headers"
  }
}

CRITICAL SEMANTIC MAPPING RULES:
For `sections_layout`, you MUST semantically map whatever heading is on the resume to one of these standardized keys:
["personalInfo", "summary", "experience", "education", "projects", "skills", "certifications", "languages", "custom"]
For example, if the resume says "Employment History", output "experience". If it says "Tech Stack", output "skills".
"""

def pdf_to_image(pdf_path: Path) -> str:
    """Convert the first page of a PDF to a base64 image string using PyMuPDF."""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        print("Error: PyMuPDF is not installed. Run: pip install pymupdf")
        sys.exit(1)

    doc = fitz.open(pdf_path)
    if len(doc) == 0:
        raise ValueError("PDF is empty")
    
    # Load first page only for layout extraction
    page = doc.load_page(0)
    # Render at 150 DPI
    pix = page.get_pixmap(matrix=fitz.Matrix(150 / 72, 150 / 72))
    img_data = pix.tobytes("png")
    return base64.b64encode(img_data).decode("utf-8")

def image_to_base64(img_path: Path) -> str:
    """Encode an image file to base64."""
    with open(img_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def get_media_type(extension: str) -> str:
    types = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}
    return types.get(extension.lower(), "image/jpeg")

def clean_json_response(content: str) -> dict:
    """Robustly extract JSON from VLM responses that might wrap it in markdown prose."""
    content = content.strip()
    
    # Strip opening fence
    if content.startswith("```"):
        content = content.split("\n", 1)[1] if "\n" in content else content[3:]
    # Strip closing fence
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()
    if content.startswith("json"):
        content = content[4:].strip()

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    # Regex fallback to find the first JSON object block
    match = re.search(r'\{[\s\S]+\}', content)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
            
    raise ValueError(f"Could not parse valid JSON from VLM output. Raw output start:\n{content[:200]}")

async def analyze_template(file_path: Path):
    """Analyze a single template file using NVIDIA NIM."""
    print(f"\nAnalyzing: {file_path.name}...")
    
    ext = file_path.suffix.lower()
    if ext == ".pdf":
        base64_img = pdf_to_image(file_path)
        media_type = "image/png"
    elif ext in [".png", ".jpg", ".jpeg", ".webp"]:
        base64_img = image_to_base64(file_path)
        media_type = get_media_type(ext)
    else:
        print(f"Skipping unsupported file type: {ext}")
        return

    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(
                "https://integrate.api.nvidia.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {VLM_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": VLM_MODEL,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a JSON-only API. Return ONLY valid JSON, no markdown formatting."
                        },
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": PROMPT},
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:{media_type};base64,{base64_img}"}
                                }
                            ]
                        }
                    ],
                    "max_tokens": 1024,
                    "temperature": 0.1,
                }
            )
            response.raise_for_status()
            data = response.json()
            raw_content = data["choices"][0]["message"]["content"]
            
            parsed_json = clean_json_response(raw_content)
            
            # Save output
            output_name = f"{file_path.stem}_spec.json"
            output_path = OUTPUTS_DIR / output_name
            
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(parsed_json, f, indent=2)
                
            print(f"Successfully extracted layout to: {output_path.relative_to(root_dir)}")
            
        except Exception as e:
            print(f"Failed to analyze {file_path.name}: {e}")

async def main():
    files = [f for f in INPUTS_DIR.iterdir() if f.is_file() and f.name != ".gitkeep"]
    
    if not files:
        print(f"No files found in {INPUTS_DIR.relative_to(root_dir)}. Please add PDF or Image templates to analyze.")
        return
        
    print(f"Starting VLM analysis for {len(files)} template(s)...")
    for file_path in files:
        await analyze_template(file_path)
        
    print("\nAll template analyses complete!")

if __name__ == "__main__":
    asyncio.run(main())
