from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

from src.pdf_utils import get_page_count, parse_page_mode_input
from src.docai_client import process_pdf_inline, save_outputs


def read_env():
    load_dotenv()  # reads .env in project root
    env = {
        "GOOGLE_APPLICATION_CREDENTIALS": os.getenv("GOOGLE_APPLICATION_CREDENTIALS", ""),
        "PROJECT_ID": os.getenv("DOC_AI_PROJECT_ID", ""),
        "LOCATION": os.getenv("DOC_AI_LOCATION", "us"),
        "PROCESSOR_ID": os.getenv("DOC_AI_PROCESSOR_ID", ""),
        "OUTPUT_DIR": os.getenv("OUTPUT_DIR", "output"),
    }
    missing = [k for k, v in env.items() if not v and k not in ("OUTPUT_DIR",)]
    if missing:
        raise SystemExit(
            "Missing required environment values in .env:\n  - "
            + "\n  - ".join(missing)
        )
    # The Google lib reads this env var automatically for auth:
    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = env["GOOGLE_APPLICATION_CREDENTIALS"]
    return env


def prompt_pdf_path() -> str:
    while True:
        pdf_path = input("Enter PDF path: ").strip().strip('"')
        if not pdf_path:
            print("Please enter a file path.")
            continue
        if not Path(pdf_path).exists():
            print("File not found. Try again.")
            continue
        if not pdf_path.lower().endswith(".pdf"):
            print("Please provide a .pdf file. Try again.")
            continue
        return pdf_path


def prompt_pages(total_pages: int):
    print(f"\nPDF has {total_pages} page(s). Choose one:")
    print("  [1] Full document")
    print("  [2] Single page")
    print("  [3] Page range (e.g. 3-7)")
    print("  [4] Specific list (e.g. 1,3,8)")
    while True:
        choice = input("Enter 1/2/3/4: ").strip()
        if choice in {"1", "2", "3", "4"}:
            break
        print("Invalid choice. Please enter 1, 2, 3, or 4.")
    if choice == "1":
        return "full", ""
    elif choice == "2":
        val = input("Enter a single page number (1-indexed): ").strip()
        return "single", val
    elif choice == "3":
        val = input("Enter a page range (e.g. 3-7): ").strip()
        return "range", val
    else:
        val = input("Enter a comma-separated list (e.g. 1,3,8): ").strip()
        return "list", val


def main():
    env = read_env()

    print("=== Google Document AI OCR (local PDF, interactive) ===")
    pdf_path = prompt_pdf_path()

    total = get_page_count(pdf_path)
    mode, value = prompt_pages(total)

    if mode == "full":
        pages = list(range(1, total + 1))
    else:
        pages = parse_page_mode_input(mode, value, total)
        if not pages:
            print("No valid pages selected; defaulting to Full.")
            pages = list(range(1, total + 1))

    print(f"\nProcessing pages: {pages if len(pages) <= 20 else f'{len(pages)} pages'}")

    doc = process_pdf_inline(
        project_id=env["PROJECT_ID"],
        location=env["LOCATION"],
        processor_id=env["PROCESSOR_ID"],
        pdf_path=pdf_path,
        pages_to_process=pages if pages else None,
    )
    json_path, text_path = save_outputs(doc, pdf_path, env["OUTPUT_DIR"])

    print("\n✅ Done.")
    print(f"JSON: {json_path}")
    print(f"Text: {text_path}")


if __name__ == "__main__":
    main()
