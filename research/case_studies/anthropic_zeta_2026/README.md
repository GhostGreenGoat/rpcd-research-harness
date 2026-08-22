# Anthropic Riemann-zeta process case study

This directory records the tooling used to inspect Anthropic's published
Riemann-zeta research process while designing the RPCD harness.

Primary source:

- https://www.anthropic.com/research/riemann-zeta

The third-party PDF and its full extracted text are intentionally excluded
from Git.  To reproduce the local extraction, download the process PDF from
the source page as `anthropic_zeta_process.pdf`, verify its SHA-256 if using
the same snapshot,

```text
EBB34C5ED65B1DC96A72BDF76068814A34DA9CEB1675624F68A2088180123ADA
```

then run:

```bash
python -m pip install pypdf
python research/case_studies/anthropic_zeta_2026/extract_pdf_text.py
```

Only the extraction helper and source metadata are redistributed here.
