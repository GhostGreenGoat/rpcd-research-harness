from pathlib import Path

from pypdf import PdfReader


SOURCE = Path(__file__).with_name("anthropic_zeta_process.pdf")
OUTPUT = Path(__file__).with_name("anthropic_zeta_process_extracted.txt")


reader = PdfReader(SOURCE)
pages = []
for index, page in enumerate(reader.pages, start=1):
    pages.append(f"===== PAGE {index} =====\n{page.extract_text() or ''}")

OUTPUT.write_text("\n\n".join(pages), encoding="utf-8")
print(f"wrote={OUTPUT} pages={len(reader.pages)} bytes={OUTPUT.stat().st_size}")
