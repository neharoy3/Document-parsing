# PDF Parsing — Core Concepts
> pdfplumber · text extraction · cleaning · regex · table extraction · chunking · export

## Why PDF Parsing is Different

PDFs prioritize visual consistency for humans, not structured machine readability.   
They do not store semantic structure. Unlike CSV, JSON, or HTML, a PDF stores:
- positioned text fragments
- drawing instructions
- coordinates

Not: headings, paragraphs, tables, or sections. These must be **reconstructed** by the parser from raw layout data. This is why PDF parsing is fundamentally harder than other formats.

Text extraction only retrieves raw content. Meaningful structure must still be inferred from layout, patterns, or heuristics.

```
Open PDF
    ↓
Inspect structure (pages, metadata, layout type)
    ↓
Extract text page by page
    ↓
Detect scanned pages (OCR flag)
    ↓
Clean extracted text
    ↓
Apply regex (sections, fields, headings)
    ↓
Chunk document (page / section / fixed-size)
    ↓
Extract tables → validate → structure
    ↓
Export → JSON / CSV
```

## 1. Reading a PDF

```python
import pdfplumber

with pdfplumber.open("input/sample.pdf") as pdf:
    print(len(pdf.pages))     # total pages
    print(pdf.metadata)       # embedded document metadata
```

A PDF is processed **page by page** — not as one object like JSON or CSV.

### Metadata
```python
pdf.metadata
# → {"Title": "...", "Author": "...", "Creator": "...", "CreationDate": "..."}
```

Useful for document organization and metadata inspection.

## 2. Schema Inspection

Before extraction, inspect the document:

```python
with pdfplumber.open("input/sample.pdf") as pdf:
    for i, page in enumerate(pdf.pages):
        text = page.extract_text()
        print(f"Page {i+1}: {len(text) if text else 'EMPTY'} chars")
```

Questions to answer:
- How many pages?
- Text-heavy or table-heavy?
- Selectable text or scanned image?
- Consistent layout or irregular?

Extraction strategy depends entirely on document structure.

## 3. Text Extraction

### Basic extraction
```python
text = page.extract_text()
```

### Layout-preserving extraction
```python
text = page.extract_text(layout=True)
```

`layout=True` preserves spatial positioning — better for multi-column documents and tables embedded in text.

PDF text is often extracted in positional order rather than human reading order, especially in multi-column documents.

### Multi-page extraction
```python
all_text = []
for page in pdf.pages:
    text = page.extract_text(layout=True)
    if text:
        all_text.append(text)

document_text = "\n".join(all_text)
```

Always check `if text:` — empty pages and scanned pages return `None`.


## 4. OCR Detection

```python
for i, page in enumerate(pdf.pages):
    text = page.extract_text()
    if not text:
        print(f"Page {i+1} may be scanned/image-based — OCR required")
```

Scanned PDFs contain images instead of selectable text. `extract_text()` returns `None` or near-empty strings. These require OCR tools (Tesseract, EasyOCR) to process — outside pdfplumber's scope.


## 5. Cleaning Extracted Text

Raw PDF text is noisy. Common issues:
- excessive line breaks
- broken spacing
- fragmented words from multi-column layouts
- headers/footers on every page

### Normalize line breaks
```python
text = text.replace("\n\n", "\n")
```

### Strip each line
```python
text = "\n".join(line.strip() for line in text.splitlines())
```

### Normalize spacing
```python
text = " ".join(text.split())
```

Cleaning strategy depends on the document. Inspect first, clean accordingly.

## 6. Regex on Extracted Text

Once text is extracted and cleaned, regex patterns from TXT parsing apply directly.

### Extract abstract
```python
match = re.search(r"Abstract(.*?)Introduction", document_text, re.DOTALL)
if match:
    abstract = match.group(1).strip()
```

`re.DOTALL` — makes `.` match newlines too. Essential for multi-line extraction.

### Detect headings
```python
headings = re.findall(r"\n([A-Z][A-Za-z0-9\s\-]{2,50})\n", document_text)
```

Heading detection via regex is heuristic — catches most headings but also false positives (figure captions, author names). Acceptable for most use cases.

### Extract structured fields
```python
# invoice ID, dates, amounts, emails — same patterns as TXT phase
invoice_id = re.search(r"Invoice\s+#(\w+)", text)
date = re.search(r"\d{4}-\d{2}-\d{2}", text)
```

PDF text extraction often involves regex-based post-processing.


## 7. Section Chunking

Split document into sections using heading positions.

```python
pattern = r"\n([A-Z][A-Za-z0-9\s\-]{2,50})\n"
matches = list(re.finditer(pattern, document_text))
sections = []

for i, match in enumerate(matches):
    heading = match.group(1).strip()
    start = match.end()
    end = matches[i+1].start() if i+1 < len(matches) else len(document_text)
    content = document_text[start:end].strip()
    sections.append({"heading": heading, "content": content})
```

`re.finditer()` — returns match objects with position data (`.start()`, `.end()`). Used to find boundaries between sections.

Result: list of `{"heading": ..., "content": ...}` dicts — structured document sections.

## 8. Page-Level Chunking

Simplest chunking strategy — one chunk per page.

```python
page_chunks = [
    {"page": i + 1, "text": text}
    for i, text in enumerate(all_text)
]
```

Most common default strategy in RAG pipelines. Each page becomes one retrievable unit.

### Fixed-size chunking
```python
chunks = [text[i:i+500] for i in range(0, len(text), 500)]
```

Used when sections are too long or when consistent chunk sizes are needed for embeddings.

### Chunking strategies comparison

| Strategy | When to use |
|----------|-------------|
| Page-level | Default, simple pipelines |
| Section-level | Structured documents with clear headings |
| Fixed-size | Embedding models with token limits |
| Paragraph-level | `text.split("\n\n")` — narrative documents |


## 9. Table Extraction

```python
tables = page.extract_tables()   # list of tables on the page
table = page.extract_table()     # first table only
```

Each table is returned as a **list of lists**:
```python
[
    ["Product", "Price", "Qty"],   # headers — row 0
    ["Mouse", "$29.99", "2"],      # data rows
    ["Keyboard", "$89.99", "1"]
]
```

### Convert to list of dicts
```python
headers = table[0]
structured_rows = []

for row in table[1:]:
    if row and len(row) == len(headers):   # skip malformed rows
        cleaned_row = [" ".join(cell.split()) if cell else "" for cell in row]
        row_dict = dict(zip(headers, cleaned_row))
        structured_rows.append(row_dict)
```

`dict(zip(headers, row))` — pairs header names with cell values, same as DictReader output.

### Table extraction caveats
Table detection in PDFs is inferred from layout positioning. Breaks on:
- merged cells
- irregular borders
- inconsistent column spacing
- scanned tables

Always validate table output — row lengths, None cells, duplicate rows.

## 10. Word-Level Layout Data

```python
words = page.extract_words()
# → [{"text": "Hello", "x0": 72.0, "top": 100.0, "x1": 95.0, ...}, ...]
```

Each word has coordinates (`x0`, `top`, `x1`, `bottom`). Useful when:
- text extraction order is wrong (multi-column layouts)
- need to identify text position (headers vs body)
- `extract_text()` produces broken output


## 11. Validation

PDF extraction is inconsistent — validation is critical.

```python
# skip empty pages
if not text:
    continue

# handle None cells in tables
cell = cell if cell else ""

# skip malformed rows
if len(row) != len(headers):
    continue

# skip empty sections
if not content.strip():
    continue
```

## 12. Exporting

Same export patterns as previous phases.

```python
# JSON — sections, structured records
with open("output/sections.json", "w") as f:
    json.dump(sections, f, indent=4)

# CSV — table data
with open("output/tables.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=all_tables[0].keys())
    writer.writeheader()
    writer.writerows(all_tables)
```

`encoding="utf-8"` — required for CSV when PDF text contains special characters.