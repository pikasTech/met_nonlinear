import pdfplumber
import os

pdf_dir = r"F:\Work\met_nonlinear_worktrees\met_nonlinear_master\docs\research\literature\pdfs"

pdfs = [
    ("Yang_2023_Floss.pdf", "Yang_2023_Floss.md"),
    ("Li_2024_FTMixer.pdf", "Li_2024_FTMixer.md"),
    ("Hoang_2026_KANELE.pdf", "Hoang_2026_KANELE.md"),
    ("Kuznetsov_2026_LUT_KAN.pdf", "Kuznetsov_2026_LUT_KAN.md"),
    ("Kuznetsov_2026_LUT_Compiled_KAN.pdf", "Kuznetsov_2026_LUT_Compiled_KAN.md"),
    ("Huang_2025_KAN_Hardware.pdf", "Huang_2025_KAN_Hardware.md"),
]

for pdf_name, md_name in pdfs:
    pdf_path = os.path.join(pdf_dir, pdf_name)
    md_path = os.path.join(pdf_dir, md_name)
    
    print(f"Converting {pdf_name}...")
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n\n"
    
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(text)
    
    pdf_size = os.path.getsize(pdf_path)
    md_size = os.path.getsize(md_path)
    print(f"  -> {md_name}: PDF={pdf_size:,} bytes, MD={md_size:,} bytes")

print("\nAll conversions complete!")
