# Google Document AI OCR – Local PDF (Interactive CLI)

Process **local PDFs** with **Google Document AI (OCR Processor)** in **online (sync)** mode.

This tool:
- Prompts for a **PDF path** at runtime.
- Detects **total pages** and lets you choose **full document**, a **single page**, a **page range**, or a **custom list**.
- Saves results into `output/run_YYYYMMDD_HHMMSS/` as:
  - `document.json` – full Document AI response
  - `text.txt` – concatenated text for all processed pages
  - `pages/page_N.txt` – per-page text
  - `SOURCE.txt` – absolute path of the source PDF

> ⚠️ **Security**: Keep your service account JSON and `.env` **out of Git**. This repo’s `.gitignore` already excludes them.

---

## Why this project?

- **Works with local PDFs**: No manual upload to GCS needed for this sample.
- **Interactive**: Choose pages on the fly.
- **Simple outputs**: Human-readable text files and raw JSON, ready for your next step (indexing, search, etc.).

> Uses **Document AI “OCR Processor”** (not the Vision PDF/TIFF async flow).

---

## Project structure

```
gdoc-ocr-sample/
├─ config/
│  └─ ocr-project.json   # your service-account key (do NOT commit)
├─ output/                                   # OCR results go here (gitignored)
├─ src/
│  ├─ docai_client.py                        # Doc AI client + save helpers
│  └─ pdf_utils.py                           # Page counting + page selection parsing
├─ main.py                                   # Entry point (run: python main.py)
├─ .env.example                              # Template for configuration
└─ requirements.txt
```

---

## Prerequisites

- **Python** 3.10+ (3.11/3.12 OK)
- A **Google Cloud project** with **Document AI API enabled**
- A **Document AI OCR Processor** created in your chosen region (e.g., `us`)
- A **Service Account** with permission to call Document AI (assign a suitable Document AI role) and a **JSON key**

### Create / locate the following values

- **Project ID** – e.g., `ocr-project`
- **Location** – region of your processor, e.g., `us`
- **Processor ID** – the ID of your OCR processor in Document AI
- **Service account JSON** – download its key file

---

## Setup

### 1) Clone & install dependencies

```bash
git clone <your-repo-url> gdoc-ocr-sample
cd gdoc-ocr-sample

python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

pip install -r requirements.txt
```

### 2) Place credentials & configure environment

1. Put your service-account key in:
   ```
   ./config/ocr-project.json
   ```
   > You can use a different filename; just make sure `.env` points to it.

2. Create your `.env` from the template and fill values:
   ```bash
   cp .env.example .env
   # Open .env and set the following:
   # GOOGLE_APPLICATION_CREDENTIALS=./config/ocr-project.json
   # DOC_AI_PROJECT_ID=ocr-project
   # DOC_AI_LOCATION=us
   # DOC_AI_PROCESSOR_ID=YOUR_OCR_PROCESSOR_ID
   ```

> The app reads `.env` automatically. No config questions at runtime.

---

## Run

```bash
python main.py
```

**Flow:**
1. The program asks for a **PDF path** (e.g., `C:\docs\sample.pdf` or `/home/me/docs/sample.pdf`).
2. It shows the **total page count** and asks how you want to proceed:
   - Full document
   - Single page (e.g., `5`)
   - Page range (e.g., `3-7`)
   - Specific list (e.g., `1,3,9`)
3. Outputs are written to `output/run_YYYYMMDD_HHMMSS/`:
   - `document.json` – raw Document AI result
   - `text.txt` – all text
   - `pages/page_*.txt` – per-page text files
   - `SOURCE.txt` – source path

---

## Example

```
$ python main.py
=== Google Document AI OCR (local PDF, interactive) ===
Enter PDF path: /home/me/docs/form.pdf

PDF has 12 page(s). Choose one:
  [1] Full document
  [2] Single page
  [3] Page range (e.g. 3-7)
  [4] Specific list (e.g. 1,3,8)
Enter 1/2/3/4: 3
Enter a page range (e.g. 3-7): 2-5

Processing pages: [2, 3, 4, 5]

✅ Done.
JSON: output/run_20250101_104233/document.json
Text: output/run_20250101_104233/text.txt
```

---

## Configuration reference (`.env`)

| Key | Description | Example |
| --- | --- | --- |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to service account JSON (absolute or relative) | `./config/ocr-project.json` |
| `DOC_AI_PROJECT_ID` | Your GCP Project ID | `ocr-project` |
| `DOC_AI_LOCATION` | Region of your processor (changes endpoint) | `us` |
| `DOC_AI_PROCESSOR_ID` | OCR Processor ID from Document AI console | `1234567890abcdef` |
| `OUTPUT_DIR` (optional) | Base folder for results | `output` |

---

## Troubleshooting

- **`Missing required environment values in .env`**  
  → Open `.env` and fill all required keys.

- **`File not found` or `Please provide a .pdf file`**  
  → Check the path you typed and confirm the extension is `.pdf`.

- **`PERMISSION_DENIED` (403) or `processor not found`**  
  → Ensure:
  - The service account has permission to call Document AI in your project.
  - `DOC_AI_LOCATION` matches the processor’s region (e.g., `us`).
  - `DOC_AI_PROCESSOR_ID` is correct.

- **`InvalidArgument` about endpoint**  
  → The app picks a regional endpoint like `us-documentai.googleapis.com` based on your `DOC_AI_LOCATION`. Make sure the location is correct for your processor.

- **Garbled characters / encoding**  
  → Outputs are UTF-8. If viewing in Windows Notepad, prefer apps that handle UTF-8 well (VS Code, Notepad++, etc.).

---

## FAQ

**Q: Can I process images (JPG/PNG) too?**  
A: This sample targets PDFs. You can extend it to accept images (switch MIME type, keep the same processor).

**Q: Can it batch a whole folder?**  
A: Yes—wrap `main()` logic in a loop over files and reuse `process_pdf_inline`. (Happy to add an example if you need it.)

**Q: Can I export a searchable PDF (text layer)?**  
A: This sample writes TXT/JSON. If you want a searchable PDF, say the word and we’ll add a writer step.

---

## Safety & secrets

- **Never commit**: `.env`, `config/*.json`, and `output/`.
- If a **private key** is exposed publicly, **revoke & rotate** it in Google Cloud IAM → Service Accounts.

---

## Contributing / License

- PRs welcome for features like batch mode, hOCR/ALTO, or PDF+text outputs.
- License: MIT (add a `LICENSE` file if you plan to open-source).
