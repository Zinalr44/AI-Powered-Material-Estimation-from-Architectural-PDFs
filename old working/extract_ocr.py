from pdf2image import convert_from_path
import pytesseract
import os
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_from_image(pdf_path):
    images = convert_from_path(pdf_path)
    extracted_text = []
    
    for img in images:
        text = pytesseract.image_to_string(img)
        extracted_text.append(text)
    
    return "\n".join(extracted_text)

if __name__ == "__main__":
    pdf_folder = "data"
    output_folder = "extracted_data"
    
    os.makedirs(output_folder, exist_ok=True)
    
    for pdf_file in os.listdir(pdf_folder):
        if pdf_file.endswith(".pdf"):
            pdf_path = os.path.join(pdf_folder, pdf_file)
            extracted_text = extract_text_from_image(pdf_path)
            
            output_file = os.path.join(output_folder, pdf_file.replace(".pdf", "_ocr.txt"))
            with open(output_file, "w", encoding="utf-8") as file:
                file.write(extracted_text)
            
            print(f"OCR extracted text saved: {output_file}")
