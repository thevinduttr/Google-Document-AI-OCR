from __future__ import annotations

import os
from typing import List, Optional, Tuple
from datetime import datetime
from pathlib import Path
from google.cloud import documentai as documentai
from google.protobuf.json_format import MessageToDict
import json


def _client_for_location(location: str) -> documentai.DocumentProcessorServiceClient:
    # DocAI uses regional endpoints; set api_endpoint accordingly.
    endpoint = f"{location}-documentai.googleapis.com"
    return documentai.DocumentProcessorServiceClient(
        client_options={"api_endpoint": endpoint}
    )


def _build_process_options(pages: Optional[List[int]]) -> Optional[documentai.ProcessOptions]:
    if not pages:
        return None
    return documentai.ProcessOptions(
        individual_page_selector=documentai.ProcessOptions.IndividualPageSelector(
            pages=pages  # 1-indexed pages
        )
    )


def process_pdf_inline(
    project_id: str,
    location: str,
    processor_id: str,
    pdf_path: str,
    pages_to_process: Optional[List[int]] = None,
) -> documentai.Document:
    """
    Processes a local PDF with Document AI OCR Processor (online mode).
    Returns the Document AI `Document` object.
    """
    client = _client_for_location(location)
    name = client.processor_path(project_id, location, processor_id)

    with open(pdf_path, "rb") as f:
        content = f.read()

    raw_document = documentai.RawDocument(content=content, mime_type="application/pdf")
    process_options = _build_process_options(pages_to_process)

    request = documentai.ProcessRequest(
        name=name,
        raw_document=raw_document,
        process_options=process_options,
    )

    result = client.process_document(request=request)
    return result.document


def save_outputs(
    doc: documentai.Document,
    original_pdf: str,
    output_dir: Optional[str] = None,
) -> Tuple[Path, Path]:
    """
    Saves:
      - Raw JSON (Document object) → document.json
      - Full text → text.txt
      - Per-page text → pages/page_N.txt
    Returns (json_path, text_path).
    """
    time_tag = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_out = Path(output_dir or "output") / f"run_{time_tag}"
    base_out.mkdir(parents=True, exist_ok=True)

    # Save JSON
    json_path = base_out / "document.json"
    as_dict = MessageToDict(doc._pb, preserving_proto_field_name=True)
    json_path.write_text(json.dumps(as_dict, ensure_ascii=False, indent=2), encoding="utf-8")

    # Save full text
    text_path = base_out / "text.txt"
    text_path.write_text(doc.text or "", encoding="utf-8")

    # Per-page text via layout anchors
    pages_dir = base_out / "pages"
    pages_dir.mkdir(exist_ok=True)
    for i, page in enumerate(doc.pages, start=1):
        page_text_chunks = []
        if page.layout and page.layout.text_anchor:
            for seg in page.layout.text_anchor.text_segments:
                start = int(seg.start_index) if seg.start_index else 0
                end = int(seg.end_index) if seg.end_index else 0
                page_text_chunks.append((doc.text or "")[start:end])
        page_text = "".join(page_text_chunks).strip()
        (pages_dir / f"page_{i}.txt").write_text(page_text, encoding="utf-8")

    (base_out / "SOURCE.txt").write_text(f"source={Path(original_pdf).resolve()}", encoding="utf-8")
    return json_path, text_path
