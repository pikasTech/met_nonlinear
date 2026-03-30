import fitz
import os

pdfs_dir = r"F:\Work\met_nonlinear_worktrees\met_nonlinear_master\docs\research\literature\pdfs"
os.chdir(pdfs_dir)

missing_md = [
    '2404.19756.pdf',
    'Busetto_2025_Nano_Drone.pdf',
    'Faroughi_2026_Symbolic_KAN.pdf',
    'Gong_2026_SWAN_Seismic.pdf',
    'Hoekstra_2026_LFR_Learning.pdf',
    'Howard_2026_SINDy_KANs.pdf',
    'Iacob_2025_Koopman_Schoukens.pdf',
    'Khodakarami_2026_Spectral_Bias.pdf',
    'Liu_2025_SKANODEs.pdf',
    'Silva_2024_REDOX_Gas.pdf',
    'Southworth_2026_Multi-layer_KAN.pdf',
    'Ullah_2026_NanoBench.pdf',
    'Wang_2025_SAMFre.pdf'
]

for pdf_name in missing_md:
    md_name = pdf_name.replace('.pdf', '.md')
    if os.path.exists(md_name):
        print(f'Skip {pdf_name} - already exists')
        continue
    try:
        doc = fitz.open(pdf_name)
        text = ''
        for page in doc:
            text += page.get_text()
        doc.close()
        if text.strip():
            with open(md_name, 'w', encoding='utf-8') as f:
                f.write(f'# {md_name.replace(".md", "")}\n\n')
                f.write(text)
            print(f'OK: {pdf_name} -> {md_name} ({len(text)} chars)')
        else:
            print(f'EMPTY: {pdf_name}')
    except Exception as e:
        print(f'ERROR: {pdf_name} - {e}')