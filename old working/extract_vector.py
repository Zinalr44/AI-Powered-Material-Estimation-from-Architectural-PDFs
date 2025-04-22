import fitz  # PyMuPDF
import pandas as pd
import os

def extract_vector_data(pdf_path):
    """Extracts detailed vector graphics information from a PDF file and returns structured data."""
    try:
        doc = fitz.open(pdf_path)  # Open the PDF
        print(f"Processing PDF: {pdf_path}")

        vector_data = []

        for page_num, page in enumerate(doc):
            drawings = page.get_drawings()
            if drawings:
                for draw in drawings:
                    vector_data.append({
                        "Page": page_num + 1,
                        "Type": draw["type"],
                        "Color": draw.get("color", "Unknown"),
                        "Fill Color": draw.get("fill", "None"),
                        "Stroke Width": draw.get("width", "Unknown"),
                        "Coordinates": draw.get("items", "Unknown")  # Raw path data
                    })
            else:
                vector_data.append({
                    "Page": page_num + 1,
                    "Type": "None",
                    "Color": "None",
                    "Fill Color": "None",
                    "Stroke Width": "None",
                    "Coordinates": "None"
                })

        return vector_data

    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return None

if __name__ == "__main__":
    pdf_folder = "data"  # Folder where PDFs are stored
    output_folder = "extracted_data"  # Folder to save extracted vector data

    os.makedirs(output_folder, exist_ok=True)  # Ensure output folder exists

    found_pdf = False

    for pdf_file in os.listdir(pdf_folder):
        if pdf_file.endswith(".pdf"):
            found_pdf = True
            pdf_path = os.path.join(pdf_folder, pdf_file)
            output_file = os.path.join(output_folder, pdf_file.replace(".pdf", "_vector_data.csv"))

            vector_data = extract_vector_data(pdf_path)

            if vector_data:
                df = pd.DataFrame(vector_data)
                df.to_csv(output_file, index=False)
                print(f"Extracted vector data saved: {output_file}")

    if not found_pdf:
        print("No PDF files found in the 'data/' folder. Please add PDFs and try again.")
