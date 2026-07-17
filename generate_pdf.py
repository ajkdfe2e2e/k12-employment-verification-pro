#!/usr/bin/env python3
"""Generate a U.S. K-12 employment verification PDF from editable HTML + JSON.

Examples:
    python generate_pdf.py --data examples/sample_letter.json --output output/sample_draft.pdf
    python generate_pdf.py --data my_teacher.json --output output/teacher_letter.pdf --final

Final mode removes the draft watermark and blocks obvious placeholders unless
--force is supplied for controlled layout testing.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import fitz  # PyMuPDF
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyMuPDF is required: python -m pip install pymupdf") from exc

try:
    from playwright.sync_api import sync_playwright
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Playwright is required. Install it with:\n"
        "  python -m pip install playwright\n"
        "  playwright install chromium"
    ) from exc


PLACEHOLDER_PATTERNS = (
    re.compile(r"\[[^\]]+\]"),
    re.compile(r"\bexample\b", re.IGNORECASE),
    re.compile(r"\.(?:test|invalid|localhost)(?:[/\s:]|$)", re.IGNORECASE),
    re.compile(r"\b555[- )]", re.IGNORECASE),
    re.compile(r"\bsample\b", re.IGNORECASE),
    re.compile(r"\bdraft\b", re.IGNORECASE),
    re.compile(r"your school", re.IGNORECASE),
    re.compile(r"placeholder", re.IGNORECASE),
    re.compile(r"test school", re.IGNORECASE),
)

REQUIRED_PATHS = (
    ("school.legalName", "School legal name"),
    ("school.displayName", "School display name"),
    ("school.addressLine1", "School street address"),
    ("school.cityStateZip", "School city/state/ZIP"),
    ("school.phone", "School phone"),
    ("school.email", "School email"),
    ("school.website", "School website"),
    ("document.issueDate", "Issue date"),
    ("document.id", "Document ID"),
    ("document.subject", "Subject"),
    ("employee.name", "Employee name"),
    ("employee.jobTitle", "Job title"),
    ("employee.status", "Employment status"),
    ("employee.startDate", "Employment start date"),
    ("signatory.name", "Signatory name"),
    ("signatory.title", "Signatory title"),
    ("signatory.phone", "Signatory phone"),
    ("signatory.email", "Signatory email"),
)


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"Data file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit("The JSON root must be an object.")
    return value


def get_path(data: dict[str, Any], path: str) -> Any:
    value: Any = data
    for key in path.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def iter_strings(value: Any, path: str = ""):
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from iter_strings(item, f"{path}.{index}" if path else str(index))
    elif isinstance(value, dict):
        for key, item in value.items():
            next_path = f"{path}.{key}" if path else key
            yield from iter_strings(item, next_path)


def server_side_validation(data: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    for path, label in REQUIRED_PATHS:
        if not str(get_path(data, path) or "").strip():
            problems.append(f"{label} is required ({path}).")

    paragraphs = get_path(data, "letter.bodyParagraphs") or []
    if not isinstance(paragraphs, list) or not any(str(item or "").strip() for item in paragraphs):
        problems.append("At least one body paragraph is required.")

    rows = get_path(data, "detailRows") or []
    if not isinstance(rows, list) or not any(
        isinstance(row, dict)
        and row.get("enabled", True)
        and (str(row.get("label", "")).strip() or str(row.get("value", "")).strip())
        for row in rows
    ):
        problems.append("At least one enabled employment detail row is required.")

    if get_path(data, "employee.includeCompensation") and not str(
        get_path(data, "employee.compensation") or ""
    ).strip():
        problems.append("Compensation is enabled but the compensation field is empty.")

    if not str(get_path(data, "verification.phone") or get_path(data, "verification.email") or "").strip():
        problems.append("A verification phone or email is required.")

    ignored_paths = {
        "document.watermarkText",
        "school.logoDataUrl",
        "school.letterheadDataUrl",
        "signatory.signatureDataUrl",
        "verification.qrDataUrl",
    }
    for path, text in iter_strings(data):
        if path in ignored_paths or path.endswith("DataUrl"):
            continue
        if any(pattern.search(text) for pattern in PLACEHOLDER_PATTERNS):
            problems.append(f"Field appears to contain sample or placeholder data: {path}")

    return problems


def find_chromium() -> str | None:
    return (
        shutil.which("chromium")
        or shutil.which("chromium-browser")
        or shutil.which("google-chrome")
        or shutil.which("google-chrome-stable")
    )


def set_pdf_metadata(pdf_path: Path, data: dict[str, Any]) -> None:
    school = str(get_path(data, "school.displayName") or get_path(data, "school.legalName") or "School")
    employee = str(get_path(data, "employee.name") or "Employee")
    letter_id = str(get_path(data, "document.id") or "")
    title = f"Employment Verification - {employee}"
    subject = f"K-12 employment verification letter; Letter ID {letter_id}".strip()
    keywords = ", ".join(filter(None, ["employment verification", "K-12", "faculty", letter_id]))

    doc = fitz.open(pdf_path)
    metadata = dict(doc.metadata or {})
    metadata.update(
        {
            "title": title,
            "author": school,
            "subject": subject,
            "keywords": keywords,
            "creator": "K-12 Employment Verification HTML/PDF Generator",
            "producer": "Chromium PDF Engine",
        }
    )
    doc.set_metadata(metadata)
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False, dir=pdf_path.parent) as handle:
        temp_path = Path(handle.name)
    try:
        doc.save(temp_path, garbage=4, deflate=True, clean=True)
        doc.close()
        temp_path.replace(pdf_path)
    finally:
        if temp_path.exists():
            temp_path.unlink(missing_ok=True)


def write_manifest(pdf_path: Path, data: dict[str, Any]) -> Path:
    pdf_hash = hashlib.sha256(pdf_path.read_bytes()).hexdigest().upper()
    manifest = {
        "schema": "k12-employment-verification-manifest/1.0",
        "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
        "documentId": get_path(data, "document.id"),
        "recordFingerprint": get_path(data, "verification.recordFingerprint"),
        "employeeName": get_path(data, "employee.name"),
        "issuingSchool": get_path(data, "school.legalName"),
        "pdfFile": pdf_path.name,
        "pdfSha256": pdf_hash,
    }
    manifest_path = pdf_path.with_suffix(pdf_path.suffix + ".manifest.json")
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    base_dir = Path(__file__).resolve().parent
    parser.add_argument("--data", required=True, type=Path, help="Editable JSON data file")
    parser.add_argument(
        "--template",
        type=Path,
        default=base_dir / "k12_employment_verification_pro_editor.html",
        help="HTML editor/template path",
    )
    parser.add_argument("--output", "-o", required=True, type=Path, help="Output PDF path")
    parser.add_argument("--final", action="store_true", help="Remove draft watermark and enforce final checks")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Bypass placeholder validation for controlled layout testing; not recommended for issuance",
    )
    parser.add_argument("--manifest", action="store_true", help="Write a SHA-256 JSON manifest next to the PDF")
    parser.add_argument("--timeout-ms", type=int, default=60_000)
    args = parser.parse_args()

    template = args.template.resolve()
    if not template.exists():
        raise SystemExit(f"Template not found: {template}")
    data = load_json(args.data.resolve())

    if args.final and not args.force:
        server_problems = server_side_validation(data)
        if server_problems:
            formatted = "\n".join(f"  - {item}" for item in server_problems)
            raise SystemExit(
                "Final PDF was not generated because the source data did not pass issuance checks:\n"
                f"{formatted}\n"
                "Replace sample values with verified school information. Use --force only for controlled testing."
            )

    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    chromium_path = find_chromium()

    with sync_playwright() as playwright:
        launch_args: dict[str, Any] = {"headless": True, "args": ["--no-sandbox", "--disable-dev-shm-usage"]}
        if chromium_path:
            launch_args["executable_path"] = chromium_path
        browser = playwright.chromium.launch(**launch_args)
        page = browser.new_page(viewport={"width": 1600, "height": 1300}, device_scale_factor=1)
        html = template.read_text(encoding="utf-8")
        vendor_path = template.parent / "vendor" / "qrcode-generator.bundle.js"
        if vendor_path.exists():
            vendor_code = vendor_path.read_text(encoding="utf-8")
            html = html.replace(
                '<script src="vendor/qrcode-generator.bundle.js"></script>',
                f'<script>{vendor_code}</script>',
            )
        page.set_content(html, wait_until="load", timeout=args.timeout_ms)
        page.wait_for_function("window.__letterReady === true", timeout=args.timeout_ms)
        page.evaluate("payload => window.setLetterData(payload)", data)
        preparation = page.evaluate("options => window.prepareForPdf(options)", {"final": args.final})

        if preparation.get("overflow"):
            browser.close()
            raise SystemExit(
                "The letter content exceeds one U.S. Letter page. Shorten the text, remove rows, "
                "reduce the base font size, or select Compact/Tight density."
            )
        if args.final and not args.force and not preparation.get("valid"):
            errors = preparation.get("errors") or ["Browser-side final validation failed."]
            browser.close()
            raise SystemExit("Final validation failed:\n" + "\n".join(f"  - {item}" for item in errors))

        rendered_data = page.evaluate("() => window.getLetterData()")
        page.emulate_media(media="print")
        page.pdf(
            path=str(output),
            format="Letter",
            print_background=True,
            prefer_css_page_size=True,
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
        )
        browser.close()

    if not output.exists() or output.stat().st_size < 10_000:
        raise SystemExit("PDF generation failed: the output is missing or unexpectedly small.")

    set_pdf_metadata(output, rendered_data)
    manifest_path = write_manifest(output, rendered_data) if args.manifest else None

    print(output)
    if manifest_path:
        print(manifest_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
