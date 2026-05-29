import fitz
import os

def extract_text_from_pdf(pdf_path:str)->str:
    
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Could not find the PDF")
    
    try:
        doc = fitz.open(pdf_path)
        extracted_text = []
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            
            blocks = page.get_text("blocks")
            text_blocks = [b for b in blocks if b[6]==0]
            
            text_blocks.sort(key=lambda b: (round(b[0]/100), b[1]))
            
            extracted_text.append(f"\n\n--- Page {page_num+1} ---\n\n")
            
            for block in text_blocks:
                clean_text = block[4].replace("-\n", "").strip()
                extracted_text.append(clean_text)
                
            doc.close()
            return "\n\n".join(extracted_text)
    except Exception as e:
        return f"An error occurred while parsing the PDF: {str(e)}"