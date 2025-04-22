import pdfplumber
import fitz  # PyMuPDF
import os

def extract_text_from_pdf(pdf_path):
    extracted_text = []
    
    with fitz.open(pdf_path) as doc:
        for page in doc:
            extracted_text.append(page.get_text("text"))  # Extract text from each page
    
    return "\n".join(extracted_text)

def save_text_to_file(text, output_path):
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(text)

if __name__ == "__main__":
    pdf_folder = "data"
    output_folder = "extracted_data"
    
    os.makedirs(output_folder, exist_ok=True)
    
    for pdf_file in os.listdir(pdf_folder):
        if pdf_file.endswith(".pdf"):
            pdf_path = os.path.join(pdf_folder, pdf_file)
            extracted_text = extract_text_from_pdf(pdf_path)
            
            output_file = os.path.join(output_folder, pdf_file.replace(".pdf", ".txt"))
            save_text_to_file(extracted_text, output_file)
            
            print(f"Extracted text saved: {output_file}")
