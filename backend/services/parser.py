import fitz 
import os

def extract_text_and_images(pdf_path: str):
    """
    Extracts text using heuristics AND extracts raw images/graphs, 
    saving them locally for document compilation.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Could not find the PDF at: {pdf_path}")

    # Create an images directory
    img_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "images")
    os.makedirs(img_dir, exist_ok=True)
    
    extracted_text = []
    saved_image_paths = []

    try:
        doc = fitz.open(pdf_path)
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            
            # --- 1. EXTRACT TEXT ---
            blocks = page.get_text("blocks")
            text_blocks = [b for b in blocks if b[6] == 0]
            text_blocks.sort(key=lambda b: (round(b[0] / 100), b[1]))
            
            extracted_text.append(f"\n\n--- PAGE {page_num + 1} ---\n\n")
            for block in text_blocks:
                clean_text = block[4].replace("-\n", "").strip()
                extracted_text.append(clean_text)
                
            # --- 2. EXTRACT IMAGES/GRAPHS ---
            image_list = page.get_images(full=True)
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                
                # Filter out tiny icons or noise (less than 10kb)
                if len(image_bytes) > 10240:
                    img_filename = f"graph_page{page_num+1}_{img_index}.{image_ext}"
                    img_filepath = os.path.join(img_dir, img_filename)
                    
                    with open(img_filepath, "wb") as f:
                        f.write(image_bytes)
                    saved_image_paths.append(img_filepath)
                
        doc.close()
        return "\n\n".join(extracted_text), saved_image_paths
        
    except Exception as e:
        print(f"Error parsing PDF: {str(e)}")
        return "", []