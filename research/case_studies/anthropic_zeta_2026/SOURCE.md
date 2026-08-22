# Source record

## Primary source

- Local-only ignored file: `anthropic_zeta_process.pdf` (not redistributed)
- PDF title metadata: *Transcripts of Claude sub-agents E2 and E2-pairs,
  typeset and annotated*
- Source URL:
  <https://www-cdn.anthropic.com/8a0d1add3c637b858a9a181e98c40e9548c3f44f.pdf>
- Retrieved: 2026-08-22 (Asia/Shanghai)
- Size: 1,952,068 bytes
- Pages: 116, US Letter, PDF 1.4, unencrypted
- SHA-256:
  `EBB34C5ED65B1DC96A72BDF76068814A34DA9CEB1675624F68A2088180123ADA`

Exact scope supported: this PDF documents two selected sub-agent runs and
selected orchestrator context. It is not the complete larger campaign, and it
does not contain the agents' private reasoning text. Yellow notes and section
banners are later editorial annotations; the white panels contain the exported
record, subject to the redactions described by the PDF.

## Derived local material

- `anthropic_zeta_process_extracted.txt`: local-only ignored UTF-8 text extracted page by page with
  explicit page markers; 357,299 bytes; SHA-256
  `D37FA02783DE5E81BCDC33A57E829241F3F4B08DACBF25AF5A4BCA1495303B5A`.
- `extract_pdf_text.py`: the reproducible extraction script, using `pypdf`.
- `SUMMARY_ZH.md`: evidence-labeled Chinese process summary and RPCD mapping.

Text extraction is for search and quotation location only. Mathematical layout
and formula order can be damaged by extraction, so formula-level claims were
checked against rendered PDF pages. Visually inspected pages: 1, 2, 3, 69, 70,
98, 107, and 115.

## Retrieval and processing log

Successful commands/tools:

- PowerShell `Invoke-WebRequest` downloaded the source URL to the local PDF.
- Poppler `pdfinfo` verified metadata and page count.
- `pypdf` extracted all 116 pages to UTF-8 text.
- Poppler `pdftoppm` rendered representative pages for visual verification.

Failed attempts retained for audit:

- Opening the CDN URL through the web reader returned an unsafe-URL error; the
  source was downloaded directly instead.
- The first inline Python extraction command failed with a quoting-induced
  `SyntaxError`; it wrote no output. It was replaced by the checked-in extraction
  script.

No mathematical conclusion in `SUMMARY_ZH.md` was inferred from a null search
result. No RPCD claim file was edited.
