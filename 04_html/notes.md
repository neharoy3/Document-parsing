# HTML Parsing — Core Concepts
> DOM traversal · scoped queries · cleaning · validation · filtering · flattening · table parsing · export

---

## HTML Parsing Pipeline

```text
 Read HTML
      ↓
 Parse DOM
      ↓
 Inspect Structure
      ↓
 Find Elements
      ↓
 Extract Values
      ↓
 Clean Data
      ↓
 Validate Records
      ↓
 Filter Relevant Data
      ↓
 Flatten Structure
      ↓
 Export Structured Output
```

HTML is semi-structured — tags provide structure, but fields may be missing, malformed, nested, or inconsistent across elements.

---

## 1. DOM Tree

BeautifulSoup parses HTML into a DOM tree — a hierarchy of nested tag objects.

```text
html
 └── body
      └── div.product-card
           ├── h3.product-name
           ├── span.price
           ├── p.description
           └── a.product-link
```

Each HTML element becomes a BeautifulSoup `Tag` object, not plain text.

Tag objects support:
- `.find()`
- `.text`
- `.get()`
- `.children`

Structure inspection should happen before extraction logic.

```python
soup.prettify()
```

prints the formatted DOM tree for inspection.

---

## 2. Parsing HTML

```python
from bs4 import BeautifulSoup

soup = BeautifulSoup(html, "html.parser")
```

`BeautifulSoup(...)` converts raw HTML into a searchable DOM tree.

---

## 3. Finding Elements

Four core querying methods:

| Method | Returns | Equivalent |
|---|---|---|
| `find()` | First matching element | `select_one()` |
| `find_all()` | List of matching elements | `select()` |
| `select_one()` | First CSS selector match | `find()` |
| `select()` | All CSS selector matches | `find_all()` |

---

## 4. Targeting Elements

### By tag

```python
soup.find("h1")
```

Examples:
- `div`
- `span`
- `h3`
- `a`
- `table`

---

### By class

```python
soup.find("div", class_="product-card")
```

`class_` is used because `class` is a reserved Python keyword.

---

### By id

```python
soup.find(id="product-table")
```

IDs are typically unique within the document.

---

### CSS selectors

```python
soup.select(".product-card")
soup.select_one("#featured")
```

Selector syntax:
- `.class`
- `#id`
- `tag`
- nested selectors

---

## 5. Scoped Queries

Two extraction styles:

### Global query

```python
soup.find(...)
```

Searches the entire document.

---

### Scoped query

```python
card.find(...)
```

Searches only inside one container element.

Common extraction pattern:

```text
find repeated containers
             ↓
extract fields inside each container
```

Each container element represents one logical record.   
Scoped extraction prevents unrelated matches from different sections of the document.

---

## 6. Extracting Values

Two primary extraction targets:

### Text content

```python
tag.text.strip()
```

Extracts visible text inside the element.  
Whitespace cleanup should happen immediately after extraction.

### Nested-text-safe extraction

```python
tag.get_text(separator=" ", strip=True)
```

Useful when inline nested tags exist.

Example:

```html
<p>
    Wireless <b>Gaming</b> Mouse
</p>
```

Preserves spacing correctly during extraction.

### Attribute extraction

```python
link.get("href")
```

Attributes store metadata on elements:
- `href`
- `src`
- `id`
- `class`
- `data-*`

`.get()` safely returns `None` if the attribute is missing.

---

## 7. Cleaning

HTML often contains:
- extra whitespace
- empty tags
- malformed sections
- missing attributes

Cleaning occurs before validation.

---

### Strip whitespace

```python
name = name.text.strip()
```

---

### Normalize internal whitespace

```python
price = "".join(price.split())
```

Converts:

```text
"$   49.99"
```

into:

```text
"$49.99"
```

Only validated records should enter the final structured dataset.

---

## 8. Filtering

HTML parsing commonly involves:
- extracting many elements
- filtering only relevant records

---

### Class-based filtering

```python
classes = card.get("class", [])

if "featured" in classes:
```

Elements may contain multiple classes:

```html
class="product-card featured"
```

`.get("class", [])` returns:

```python
["product-card", "featured"]
```

---

### Compound class filtering

```python
soup.find_all(
    "div",
    class_="product-card featured"
)
```

Targets elements containing all specified classes.

---

## 9. Flattening

HTML structures are hierarchical. Export systems usually require flat structured records.

Example transformation:

```text
nested HTML structure
    ↓
flat dictionary
```

Example:

```python
{
    "name": name,
    "category": category,
    "price": price,
    "rating": rating,
    "url": href
}
```

One container element becomes one structured record.

---

## 10. Table Parsing

HTML tables follow positional structure.

Hierarchy:

```text
table
 └── tr (row)
      └── td (cell)
```

---

### Extract rows

```python
rows = table.find_all("tr")
```

---

### Extract cells

```python
cells = row.find_all("td")
```

---

### Skip header row

```python
rows[1:]
```

because:

```python
rows[0]
```

contains column headers.

---

### Positional extraction

```python
cells[0]
cells[1]
cells[2]
```

Table parsing relies on column position rather than key-based access.

---

## 11. Traversal

Traversal navigates the DOM tree structure.

### Parent traversal

```python
tag.parent
```

Moves upward in the tree.

### Children traversal

```python
tag.children
```

Returns direct child nodes.

Traversal is primarily used for structural inspection and contextual navigation.

---

## 12. Fetching Live HTML

### Fetch webpage

```python
import requests

response = requests.get(url)
```

### Access raw HTML

```python
html = response.text
```

---

### Parse fetched HTML

```python
soup = BeautifulSoup(html, "lxml")
```

- `requests` retrieves the document
- `BeautifulSoup` parses the document

---

## 13. Export

Flattened structured records can be exported directly.

### JSON export

```python
json.dump(data, f, indent=4)
```

---

### CSV export

```python
writer = csv.DictWriter(...)
```

then:

```python
writer.writeheader()
writer.writerows(data)
```

---

## CSV vs JSON vs HTML

| | CSV | JSON | HTML |
|---|---|---|---|
| Structure | Flat | Hierarchical | Semi-structured |
| Organization | Rows/columns | Dicts/lists | Tags/classes/attributes |
| Missing values | Empty string | Missing key / `null` | Missing tag / empty text |
| Access style | `row["column"]` | `dict["key"]` | `.find()` / `.get()` |
| Repeated records | Rows | List items | Repeated containers |