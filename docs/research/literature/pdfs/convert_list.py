#!/usr/bin/env python3
import pdfplumber
from pathlib import Path

PDF_DIR = Path(r"F:\Work\met_nonlinear_worktrees\met_nonlinear_master\docs\research\literature\pdfs")
PDFS = [
    ("FIRE_He_2025.pdf", "FIRE_He_2025.md"),
    ("FreDF_Wang_2025_ICLR.pdf", "FreDF_Wang_2025_ICLR.md"),
    ("FreLE_Sun_2025.pdf", "FreLE_Sun_2025.md"),
    ("KFS_Wu_2025.pdf", "KFS_Wu_2025.md"),
    ("OLMA_Shi_2025.pdf", "OLMA_Shi_2025.md"),
    ("PETSA_Medeiros_2025_ICML.pdf", "PETSA_Medeiros_2025_ICML.md"),
    ("SAMFre_Wang_2025.pdf", "SAMFre_Wang_2025.md"),
    ("KAN_AD_2025.pdf", "KAN_AD_2025.md"),
]

def pdf_to_markdown(pdf_path, output_path):
    with pdfplumber.open(pdf_path) as pdf:
        content = []
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                content.append(f"# Page {i+1}\n\n{text}")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n\n---\n\n'.join(content))

print("Converting PDFs to Markdown...")
print("=" * 60)
for pdf_name, md_name in PDFS:
    pdf_path = PDF_DIR / pdf_name
    md_path = PDF_DIR / md_name
    try:
        pdf_to_markdown(pdf_path, md_path)
        pdf_size = pdf_path.stat().st_size
        md_size = md_path.stat().st_size
        print(f"  [OK] {md_name}: PDF={pdf_size:,} bytes, MD={md_size:,} bytes")
    except Exception as e:
        print(f"  [FAIL] {pdf_name}: {e}")
print("=" * 60)
print("Done!")