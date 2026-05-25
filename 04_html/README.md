# HTML Parsing

Parses a semi-structured HTML document through a full pipeline:

- inspects DOM structure before processing
- finds and extracts data from repeated container elements
- cleans and validates extracted records
- filters, flattens, and exports structured output

## Pipeline

```text
  Read
    ↓
  Parse
    ↓
 Inspect
    ↓
   Find
    ↓
 Extract
    ↓
  Clean
    ↓
 Validate
    ↓
  Filter
    ↓
 Flatten
    ↓
  Export
```

## Concepts Learned

- HTML parsing with `BeautifulSoup`
- DOM tree structure and inspection
- Finding elements by tag, class, id, and CSS selector
- `find()`, `find_all()`, `select()`, `select_one()`
- Scoped vs global element queries
- Text extraction and attribute extraction
- Safe attribute access with `.get()`
- Cleaning malformed and inconsistent fields
- Class-based filtering and compound class membership
- DOM traversal (`parent`, `children`)
- HTML table parsing (`tr` / `td`)
- Flattening nested tag structures into flat dicts
- Live HTML fetching with `requests`
- Export to CSV and JSON

## Notes

Detailed HTML parsing notes available here: [HTML Parsing Notes](notes.md)