# PDF Parsing

PDF document parsing using pdfplumber — text extraction, section chunking, table extraction, and structured export.

## Requirements

- `pdfplumber` — text and table extraction

Install dependencies:
```bash
pip install -r requirements.txt
```
## Parsing Pipeline

Open PDF  
→ Extract text page-by-page  
→ Clean and normalize text  
→ Detect structure using regex  
→ Chunk pages/sections  
→ Extract and validate tables  
→ Export structured data (JSON/CSV)

## Concepts Learned

- Reading PDFs with pdfplumber
- Metadata extraction
- Page-by-page text extraction
- Detection of scanned/image-based pages
- Text cleaning and normalization
- Regex extraction (abstract, headings, structured fields)
- Section chunking with `re.finditer()`
- Page-level chunking for RAG pipelines
- Table extraction and structuring
- Word-level positional layout analysis
- Export to JSON and CSV

## Key Concept

PDFs store positioned text fragments — not semantic structure. Parsing a PDF means reconstructing paragraphs, sections, and tables from raw layout data. Extraction quality depends entirely on how the source PDF was generated.


## Notes

Detailed PDF parsing notes available here: [PDF Parsing Notes](notes.md)

## Resource
[Sample PDF (Research Paper)](https://arxiv.org/pdf/2501.01110v1)