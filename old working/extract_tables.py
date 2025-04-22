import pdfplumber
import pandas as pd
import os

def extract_tables_from_pdf(pdf_path):
    tables = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted_table = page.extract_table()
            if extracted_table:
                tables.append(pd.DataFrame(extracted_table[1:], columns=extracted_table[0]))  # Convert to DataFrame
    
    return tables

if __name__ == "__main__":
    pdf_folder = "data"
    output_folder = "extracted_data"
    
    os.makedirs(output_folder, exist_ok=True)
    
    for pdf_file in os.listdir(pdf_folder):
        if pdf_file.endswith(".pdf"):
            pdf_path = os.path.join(pdf_folder, pdf_file)
            tables = extract_tables_from_pdf(pdf_path)
            
            for idx, table in enumerate(tables):
                output_file = os.path.join(output_folder, f"{pdf_file.replace('.pdf', '')}_table_{idx}.csv")
                table.to_csv(output_file, index=False)
                
                print(f"Extracted table saved: {output_file}")
