from __future__ import annotations
from typing import List
from PyPDF2 import PdfReader


def get_page_count(pdf_path: str) -> int:
    reader = PdfReader(pdf_path)
    return len(reader.pages)


def parse_page_mode_input(mode: str, user_input: str, total_pages: int) -> List[int]:
    """
    mode: 'full' | 'single' | 'range' | 'list'
    user_input:
      - single: "5"
      - range: "3-7"
      - list: "1,3,8"
    Returns a 1-indexed unique-sorted page list.
    """
    if mode == "full":
        return list(range(1, total_pages + 1))

    pages: List[int] = []
    if mode == "single":
        pages = [int(user_input)]
    elif mode == "range":
        start, end = user_input.split("-", 1)
        pages = list(range(int(start), int(end) + 1))
    elif mode == "list":
        pages = [int(x.strip()) for x in user_input.split(",") if x.strip()]
    else:
        raise ValueError("Invalid mode")

    pages = [p for p in pages if 1 <= p <= total_pages]
    return sorted(list(set(pages)))
