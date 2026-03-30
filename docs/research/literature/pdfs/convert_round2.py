import pdfplumber
import os
from pathlib import Path

PDF_DIR = Path(r"F:\Work\met_nonlinear_worktrees\met_nonlinear_master\docs\research\literature\pdfs")
PDFS = [
    ("2404.19756.pdf", "Liu_2024_KAN_original.md"),
    ("Pozdnyakov_2025_lmKAN.pdf", "Pozdnyakov_2025_lmKAN.md"),
    ("Rather_2025_KAN_GRU.pdf", "Rather_2025_KAN_GRU.md"),
    ("Revay_2021_Recurrent_Equilibrium.pdf", "Revay_2021_Recurrent_Equilibrium.md"),
    ("Rufolo_2024_WH_Transformer.pdf", "Rufolo_2024_WH_Transformer.md"),
    ("SAMFre_Wang_2025.pdf", "SAMFre_Wang_2025.md"),
    ("Shen_2026_KAN_FIF.pdf", "Shen_2026_KAN_FIF.md"),
    ("Shi_2025_OLMA.pdf", "Shi_2025_OLMA.md"),
    ("Shuai_2024_PIKAN.pdf", "Shuai_2024_PIKAN.md"),
    ("Somvanshi_2025_KAN_Survey.pdf", "Somvanshi_2025_KAN_Survey.md"),
    ("Subich_2025.pdf", "Subich_2025_FreDF_double_penalty.md"),
    ("Sun_2025_FreLE.pdf", "Sun_2025_FreLE.md"),
    ("Vaca_Rubio_2024_KAN_Time_Series.pdf", "Vaca_Rubio_2024_KAN_Time_Series.md"),
    ("Voit_2024_Multikernel_NN.pdf", "Voit_2024_Multikernel_NN.md"),
    ("Wahlberg_2015_stochastic_Wiener.pdf", "Wahlberg_2015_stochastic_Wiener.md"),
    ("Wang_2024_SpectralKAN.pdf", "Wang_2024_SpectralKAN.md"),
    ("Wang_2025_WaveTuner.pdf", "Wang_2025_WaveTuner.md"),
    ("Willemstein_2023_WH_Piezoresistive.pdf", "Willemstein_2023_WH_Piezoresistive.md"),
    ("Yang_2023_Floss.pdf", "Yang_2023_Floss.md"),
    ("Yu_2025_PolyKAN.pdf", "Yu_2025_PolyKAN.md"),
    ("Yu_2025_SATL.pdf", "Yu_2025_SATL.md"),
    ("Zeng_2025_AR_KAN.pdf", "Zeng_2025_AR_KAN.md"),
    ("Zhang_2026_Time_TK.pdf", "Zhang_2026_Time_TK.md"),
    ("van_Meer_2025_Hall_sensor_Wiener.pdf", "van_Meer_2025_Hall_sensor_Wiener.md"),
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