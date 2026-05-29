import os
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

def create_reconstructed_document(abstract_text: str, insights, output_filename: str = "Reconstructed_Paper.docx"):
    """
    Takes the reconstructed text chunks and the structured Pydantic insights,
    and generates a professional, well-styled Microsoft Word document.
    """
    doc = Document()
    
    # 1. Page Formatting / Styling
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Arial'
    font.size = Pt(11)
    
    # 2. Document Title
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title.add_run("AI RECONSTRUCTION REPORT")
    title_run.font.name = 'Arial'
    title_run.font.size = Pt(18)
    title_run.bold = True
    
    doc.add_paragraph("\n") # Spacing
    
    # 3. Section 1: Core Insights (Structured Table)
    h1 = doc.add_heading(level=1)
    h1_run = h1.add_run("1. Executive Technical Summary")
    h1_run.font.name = 'Arial'
    h1_run.bold = True
    
    doc.add_paragraph(f"Core Scientific Contribution: {insights.core_contribution}")
    
    # Create an elegant technical table for metadata
    table = doc.add_table(rows=1, cols=2)
    table.style = 'Light Shading Accent 1'
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Technical Dimension'
    hdr_cells[1].text = 'Extracted Detail'
    
    # Populate Architecture Row
    row_cells = table.add_row().cells
    row_cells[0].text = 'Proposed Architecture'
    row_cells[1].text = insights.architecture
    
    # Populate Datasets Row
    row_cells = table.add_row().cells
    row_cells[0].text = 'Target Evaluation Domains / Datasets'
    row_cells[1].text = ", ".join(insights.datasets) if insights.datasets else "None Specified"
    
    doc.add_paragraph("\n") # Spacing
    
    # 4. Section 2: Reconstructed Abstract
    h2 = doc.add_heading(level=1)
    h2_run = h2.add_run("2. Reconstructed Literature Abstract")
    h2_run.font.name = 'Arial'
    h2_run.bold = True
    
    # Add the text paragraph and justify it for a clean paper layout
    p_abstract = doc.add_paragraph()
    p_abstract.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_abstract.add_run(abstract_text)
    
    # 5. Ensure the data output directory exists and save
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
    os.makedirs(output_dir, exist_ok=True)
    
    file_path = os.path.join(output_dir, output_filename)
    doc.save(file_path)
    return file_path