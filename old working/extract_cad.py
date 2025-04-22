import os
import subprocess
import ezdxf
import pandas as pd

# Define Inkscape Path (Update if installed elsewhere)
INKSCAPE_PATH = r"C:\Program Files\Inkscape\bin\inkscape.exe"

def convert_pdf_to_dxf(pdf_path, dxf_path):
    """Converts a PDF to DXF using Inkscape."""
    try:
        print(f"🔄 Converting {pdf_path} to DXF...")
        command = f'"{INKSCAPE_PATH}" "{pdf_path}" --export-filename="{dxf_path}"'
        subprocess.run(command, shell=True, check=True)
        print(f"✅ Conversion complete: {dxf_path}")
        return True
    except FileNotFoundError:
        print("❌ Error: Inkscape not found. Ensure it's installed and added to system PATH.")
        return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Error converting PDF to DXF: {e}")
        return False

def detect_dxf_units(doc):
    """Detect DXF units and return scaling factor to feet."""
    unit_mapping = {1: 1, 2: 0.0833, 3: 0.00328, 4: 0.03937, 5: 1.09361}
    dxf_units = doc.header.get("$INSUNITS", 1)
    scale_factor = unit_mapping.get(dxf_units, 1)
    print(f"📏 DXF Units Detected: {dxf_units} → Scaling Factor: {scale_factor}")
    return scale_factor

def extract_layers(dxf_path):
    """List all layers in the DXF file for debugging."""
    dxf_path = os.path.abspath(dxf_path)
    if not os.path.exists(dxf_path):
        print(f"❌ Error: DXF file not found: {dxf_path}")
        return []

    try:
        doc = ezdxf.readfile(dxf_path)
        layers = [layer.dxf.name for layer in doc.layers]
        print(f"📜 Available Layers: {layers}")
        return layers
    except Exception as e:
        print(f"❌ Error reading DXF file: {e}")
        return []

def extract_rooms_from_dxf(dxf_path):
    """Extract room names from TEXT, MTEXT, BLOCKS, ATTRIBUTES, DIMENSIONS, HATCH, and LEADER."""
    doc = ezdxf.readfile(dxf_path)
    msp = doc.modelspace()
    rooms = []

    print(f"🔍 Extracting Room Data from DXF: {dxf_path}")

    for entity in msp.query("TEXT MTEXT INSERT DIMENSION HATCH LEADER"):
        room_name = None
        layer = entity.dxf.layer
        x, y = None, None

        if entity.dxftype() == "TEXT":
            room_name = entity.dxf.text.strip()
            x, y = entity.dxf.insert.x, entity.dxf.insert.y
        elif entity.dxftype() == "MTEXT":
            room_name = entity.plain_text().strip()
            x, y = entity.dxf.insert.x, entity.dxf.insert.y
        elif entity.dxftype() == "INSERT" and entity.has_attribs:
            for attrib in entity.attribs:
                room_name = attrib.dxf.text.strip()
                x, y = entity.dxf.insert.x, entity.dxf.insert.y
        elif entity.dxftype() == "DIMENSION":
            room_name = entity.dxf.text.strip()
            x, y = entity.dxf.defpoint.x, entity.dxf.defpoint.y
        elif entity.dxftype() == "HATCH":
            room_name = f"HATCH_{entity.dxf.handle}"
            x, y = None, None
        elif entity.dxftype() == "LEADER":
            room_name = f"Leader_{entity.dxf.handle}"
            x, y = entity.vertices[0].x, entity.vertices[0].y

        if room_name:
            rooms.append({"Room": room_name, "Layer": layer, "X": x, "Y": y, "Source": entity.dxftype()})

    if not rooms:
        print("⚠️ No room labels detected. Check DXF layers and annotation settings.")

    df = pd.DataFrame(rooms)
    output_file = os.path.join("extracted_data", os.path.basename(dxf_path).replace(".dxf", "_room_data.csv"))
    df.to_csv(output_file, index=False)
    print(f"✅ Room data saved: {output_file}")

def extract_areas_from_dxf(dxf_path):
    """Extracts areas from DXF using LWPOLYLINE, CIRCLE, and HATCH."""
    try:
        doc = ezdxf.readfile(dxf_path)
        msp = doc.modelspace()
        scale_factor = detect_dxf_units(doc)
        areas = []

        print(f"🔍 Processing DXF: {dxf_path}")

        for entity in msp.query("LWPOLYLINE CIRCLE HATCH"):
            area = None
            if entity.dxftype() == "LWPOLYLINE":
                area = entity.area * (scale_factor ** 2)
            elif entity.dxftype() == "CIRCLE":
                radius = entity.dxf.radius * scale_factor
                area = 3.1416 * (radius ** 2)
            elif entity.dxftype() == "HATCH":
                area = "HATCH_AREA"

            if area:
                areas.append({"Entity": entity.dxftype(), "Layer": entity.dxf.layer, "Area (sq ft)": area})
                print(f"✅ Extracted {entity.dxftype()} area: {area} sq ft")

        df = pd.DataFrame(areas)
        output_file = os.path.join("extracted_data", os.path.basename(dxf_path).replace(".dxf", "_cad_area.csv"))
        df.to_csv(output_file, index=False)
        print(f"✅ Extracted CAD areas saved: {output_file}")

    except Exception as e:
        print(f"❌ Error processing {dxf_path}: {e}")

if __name__ == "__main__":
    dxf_folder = "extracted_data"
    output_folder = "extracted_data"
    os.makedirs(output_folder, exist_ok=True)

    dxf_files = [f for f in os.listdir(dxf_folder) if f.endswith(".dxf")]
    print(f"🔍 Found DXF Files: {dxf_files}")

    if not dxf_files:
        print("❌ No DXF files found. Please add DXF or PDF files to 'data/' folder.")
        exit(1)

    for dxf_file in dxf_files:
        dxf_path = os.path.abspath(os.path.join(dxf_folder, dxf_file))
        extract_layers(dxf_path)
        extract_rooms_from_dxf(dxf_path)
        extract_areas_from_dxf(dxf_path)
