import pdfplumber
import os
from pathlib import Path

PDF_DIR = Path(r"F:\Work\met_nonlinear_worktrees\met_nonlinear_master\docs\research\literature\pdfs")
PDFS = [
    ("Rufolo_2024_WH_Transformer.pdf", "Rufolo_2024_WH_Transformer.md"),
    ("Voit_2024_Multikernel_NN.pdf", "Voit_2024_Multikernel_NN.md"),
    ("Revay_2021_Recurrent_Equilibrium.pdf", "Revay_2021_Recurrent_Equilibrium.md"),
    ("Willemstein_2023_WH_Piezoresistive.pdf", "Willemstein_2023_WH_Piezoresistive.md"),
]

def extract_text_from_pdf(pdf_path):
    text_parts = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                text_parts.append(f"# Page {i+1}\n\n{text}")
    return "\n\n---\n\n".join(text_parts)

for pdf_name, md_name in PDFS:
    pdf_path = PDF_DIR / pdf_name
    md_path = PDF_DIR / md_name
    print(f"Converting: {pdf_name}")
    try:
        text = extract_text_from_pdf(pdf_path)
        md_path.write_text(text, encoding="utf-8")
        pdf_size = pdf_path.stat().st_size
        md_size = md_path.stat().st_size
        print(f"  -> {md_name}: PDF={pdf_size:,} bytes, MD={md_size:,} bytes")
    except Exception as e:
        print(f"  ERROR: {e}")
print("Done.")
