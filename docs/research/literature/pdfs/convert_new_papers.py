import pdfplumber
import os
from pathlib import Path

PDF_DIR = Path(r"F:\Work\met_nonlinear_worktrees\met_nonlinear_master\docs\research\literature\pdfs")
PDFS = [
    ("Fang_2024_nonlinearity_sensitivity_Measurement.pdf", "Fang_2024_nonlinearity_sensitivity.md"),
    ("Rodriguez_Linhares_2025_Freq_Dependent_Linearizers.pdf", "Rodriguez_Linhares_2025_Freq_Dependent_Linearizers.md"),
    ("Fasmin_2017_Nonlinear_EIS.pdf", "Fasmin_2017_Nonlinear_EIS.md"),
]

def extract_text_from_pdf(pdf_path):
    text_parts = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                text_parts.append(f"# Page {i+1}\n\n{text}")
    return "\n\n---\n\n".join(text_parts)

success_count = 0
error_count = 0

for pdf_name, md_name in PDFS:
    pdf_path = PDF_DIR / pdf_name
    md_path = PDF_DIR / md_name

    if md_path.exists():
        print(f"SKIP (already exists): {md_name}")
        continue

    if not pdf_path.exists():
        print(f"SKIP (PDF not found): {pdf_name}")
        continue

    print(f"Converting: {pdf_name} -> {md_name}")
    try:
        text = extract_text_from_pdf(pdf_path)
        md_path.write_text(text, encoding="utf-8")
        pdf_size = pdf_path.stat().st_size
        md_size = md_path.stat().st_size
        print(f"  -> SUCCESS: {md_size:,} bytes (PDF was {pdf_size:,} bytes)")
        success_count += 1
    except Exception as e:
        print(f"  ERROR: {e}")
        error_count += 1

print(f"\nDone. Success: {success_count}, Errors: {error_count}")