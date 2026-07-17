# K-12 Employment Verification Letter Pro

U.S. Letter (8.5 × 11 in) **Employment Verification Letter** template for authorized K-12 school HR / principal offices.

- **Online editor (GitHub Pages):** open this repository’s Pages URL, or open `k12_employment_verification_pro_editor_singlefile.html` locally in Chrome / Edge.
- **Batch PDF:** `generate_pdf.py` + Playwright + PyMuPDF.
- **Version:** see `VERSION.txt` (2.0.0).

> Sample data uses reserved domains and 555 demo phone numbers. Final issuance checks block placeholder / sample content. This is **not** a CA digital signature platform.

## Quick start (browser)

1. Open `k12_employment_verification_pro_editor_singlefile.html` (self-contained, offline).
2. Edit school / employee / signatory fields; upload logo & signature if needed.
3. Draft: **Print / Save Draft PDF**. Final: **Validate & Print Final**.
4. Print dialog: Destination = Save as PDF, Paper = Letter, Scale = 100%, Margins = None, Background graphics = On.

中文完整说明见 [README_CN.md](./README_CN.md)，字段路径见 [FIELD_REFERENCE_CN.md](./FIELD_REFERENCE_CN.md)。

## Quick start (Python PDF)

```bash
python -m pip install -r requirements.txt
playwright install chromium

# Draft
python generate_pdf.py --data examples/sample_letter.json --output output/teacher_letter_draft.pdf --manifest

# Final (strict checks; sample JSON will fail on purpose)
python generate_pdf.py --data your_real_data.json --output output/teacher_letter.pdf --final --manifest
```

## Repository layout

```text
.
├── index.html                                          # Pages entry → singlefile editor
├── k12_employment_verification_pro_editor_singlefile.html
├── k12_employment_verification_pro_editor.html
├── generate_pdf.py
├── requirements.txt
├── vendor/qrcode-generator.bundle.js
├── examples/blank_letter.json
├── examples/sample_letter.json
└── output/sample_employment_verification_pro_draft.pdf
```

## Disclaimer

Only authorized school staff should issue official letters. Use legal school name, official domain email, and independently callable phone numbers. Salary and license numbers require employee authorization when needed. Do not add seals, accreditations, or government marks the school does not hold.

Third-party notices: [THIRD_PARTY_NOTICES.txt](./THIRD_PARTY_NOTICES.txt).
