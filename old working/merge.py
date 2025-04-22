import os
import subprocess
import ezdxf
import pandas as pd
import fitz  # PyMuPDF for vector extraction
import cv2
import pytesseract
from ultralytics import YOLO

# 🛠️ CONFIGURATION
INKSCAPE_PATH = r"C:\Program Files\Inkscape\bin\inkscape.exe"
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

# 📌 DXF UNIT MAPPING
DXF_UNIT_TO_FEET = {1: 1, 2: 0.0833, 3: 0.00328, 4: 0.03937, 5: 1.09361}

# 📌 MATERIAL RATES (Per 100 sq ft)
MATERIAL_RATES = {
    "Cement (bags)": 8,
    "Paint (gallons)": 1 / 3.5,
    "Tiles (boxes)": 1,
    "Bricks (units)": 1200,
    "Sand (cubic meters)": 0.6,
    "Steel (kg)": 10,
    "Concrete (cubic meters)": 0.5,
    "Glass (sq ft)": 2,
    "Wood (sq ft)": 5,
    "Plaster (kg)": 10
}

# ✅ FUNCTION: Convert PDF to DXF using Inkscape
def convert_pdf_to_dxf(pdf_path, dxf_path):
    try:
        print(f"🔄 Converting {pdf_path} to DXF...")
        command = f'"{INKSCAPE_PATH}" "{pdf_path}" --export-filename="{dxf_path}"'
        subprocess.run(command, shell=True, check=True)
        print(f"✅ Conversion complete: {dxf_path}")
        return True
    except Exception as e:
        print(f"❌ Error converting PDF to DXF: {e}")
        return False

# ✅ FUNCTION: Detect DXF Units
def detect_dxf_units(doc):
    dxf_units = doc.header.get("$INSUNITS", 1)
    scale_factor = DXF_UNIT_TO_FEET.get(dxf_units, 1)
    print(f"📏 DXF Units Detected: {dxf_units} → Scaling Factor: {scale_factor}")
    return scale_factor

# ✅ FUNCTION: Extract Room Names
def extract_rooms_from_dxf(dxf_path):
    doc = ezdxf.readfile(dxf_path)
    msp = doc.modelspace()
    rooms = []

    print(f"🔍 Extracting Room Data from DXF: {dxf_path}")

    for entity in msp.query("TEXT MTEXT"):
        room_name = entity.dxf.text.strip() if entity.dxftype() == "TEXT" else entity.plain_text().strip()
        x, y = entity.dxf.insert.x, entity.dxf.insert.y
        rooms.append({"Room": room_name, "X": x, "Y": y})

    if not rooms:
        print("⚠️ No room labels detected. Using AI-based detection.")
        detect_rooms_ai(dxf_path)

    df = pd.DataFrame(rooms)
    df.to_csv("extracted_data/room_data.csv", index=False)
    print(f"✅ Room data saved: extracted_data/room_data.csv")

# ✅ FUNCTION: AI-Based Room Detection (YOLO)
def detect_rooms_ai(image_path):
    model = YOLO("yolov8.pt")
    results = model(image_path)

    detected_rooms = []
    for box in results.xyxy[0]:  
        x1, y1, x2, y2, conf, cls = box
        detected_rooms.append({"Room": f"Room_{cls}", "X": (x1+x2)/2, "Y": (y1+y2)/2})

    df = pd.DataFrame(detected_rooms)
    df.to_csv("extracted_data/detected_rooms.csv", index=False)
    print("✅ AI-Based Room Detection Completed.")

# ✅ FUNCTION: Extract Material Data from DXF Layers
def extract_materials_from_dxf(dxf_path):
    doc = ezdxf.readfile(dxf_path)
    msp = doc.modelspace()
    materials = []

    for entity in msp:
        material_type = "Unknown"
        layer_name = entity.dxf.layer

        if "Brick" in layer_name:
            material_type = "Brick Wall"
        elif "Concrete" in layer_name:
            material_type = "Concrete"
        elif "Tile" in layer_name:
            material_type = "Tile Flooring"

        if entity.dxftype() == "HATCH":
            material_type = "Hatch Pattern"

        if material_type != "Unknown":
            materials.append({"Layer": layer_name, "Material Type": material_type})

    df = pd.DataFrame(materials)
    df.to_csv("extracted_data/material_data.csv", index=False)
    print("✅ Extracted Material Data Saved.")

# ✅ FUNCTION: Estimate Material Consumption
def estimate_materials():
    input_file = "extracted_data/sample_cad_area.csv"
    output_file = "extracted_data/material_estimation.csv"

    if not os.path.exists(input_file):
        print("❌ CAD area file not found. Run `extract_cad.py` first.")
        return

    df = pd.read_csv(input_file)
    total_area = df["Area (sq ft)"].sum()

    print(f"📏 Total extracted area: {total_area:.2f} sq ft")

    materials = {"Total Area (sq ft)": total_area}
    for material, rate in MATERIAL_RATES.items():
        materials[material] = (total_area / 100) * rate

    pd.DataFrame([materials]).to_csv(output_file, index=False)
    print(f"✅ Material estimation saved: {output_file}")

# ✅ FUNCTION: Extract Vector Data from PDF (Using PyMuPDF)
def extract_vector_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    extracted_text = []

    for page in doc:
        extracted_text.append(page.get_text("text"))

    with open("extracted_data/vector_data.txt", "w") as f:
        f.write("\n".join(extracted_text))

    print("✅ Vector Data Extracted from PDF.")

# ✅ FUNCTION: Extract OCR Data from PDF
def extract_ocr_from_pdf(pdf_path):
    images = convert_from_path(pdf_path)
    text_data = []

    for img in images:
        text = pytesseract.image_to_string(img)
        text_data.append(text)

    with open("extracted_data/ocr_data.txt", "w") as f:
        f.write("\n".join(text_data))

    print("✅ OCR Data Extracted from PDF.")

# ✅ MAIN EXECUTION
if __name__ == "__main__":
    data_folder = "data"
    dxf_folder = "extracted_data"

    os.makedirs(dxf_folder, exist_ok=True)

    dxf_files = [f for f in os.listdir(dxf_folder) if f.endswith(".dxf")]
    pdf_files = [f for f in os.listdir(data_folder) if f.endswith(".pdf")]

    if not dxf_files and pdf_files:
        for pdf_file in pdf_files:
            pdf_path = os.path.join(data_folder, pdf_file)
            dxf_path = os.path.join(dxf_folder, pdf_file.replace(".pdf", ".dxf"))
            convert_pdf_to_dxf(pdf_path, dxf_path)
            dxf_files.append(dxf_path)

    for dxf_file in dxf_files:
        dxf_path = os.path.abspath(os.path.join(dxf_folder, dxf_file))
        extract_rooms_from_dxf(dxf_path)
        extract_materials_from_dxf(dxf_path)

    for pdf_file in pdf_files:
        pdf_path = os.path.join(data_folder, pdf_file)
        extract_vector_from_pdf(pdf_path)
        extract_ocr_from_pdf(pdf_path)

    estimate_materials()
    print("✅ Full Process Completed.")
