import pdfplumber
import os

pdf_dir = r"F:\Work\met_nonlinear_worktrees\met_nonlinear_master\docs\research\literature\pdfs"

pdfs_to_convert = [
    ("Huang_2025_TimeKAN.pdf", "Huang_2025_TimeKAN.md"),
    ("Shuai_2024_PIKAN.pdf", "Shuai_2024_PIKAN.md"),
    ("Wang_2024_SpectralKAN.pdf", "Wang_2024_SpectralKAN.md"),
    ("Li_2024_KA_GNN.pdf", "Li_2024_KA_GNN.md"),
]

for pdf_name, md_name in pdfs_to_convert:
    pdf_path = os.path.join(pdf_dir, pdf_name)
    md_path = os.path.join(pdf_dir, md_name)
    
    print(f"Converting {pdf_name}...")
    text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)
    
    full_text = "\n\n".join(text)
    
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# {md_name.replace('.md', '')}\n\n")
        f.write(full_text)
    
    pdf_size = os.path.getsize(pdf_path)
    md_size = os.path.getsize(md_path)
    print(f"  -> {md_name}: {md_size} bytes (PDF: {pdf_size} bytes)")

print("\nDone!")
