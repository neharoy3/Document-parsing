# CSV Parsing — Core Concepts
```
Raw CSV
    ↓
Schema Inspection
    ↓
Cleaning
    ↓
Validation
    ↓
Filtering
    ↓
Sorting
    ↓
Analytics
    ↓
Export
```
---

## 1. csv.DictReader

Reads each row as a dictionary — column name as key, cell value as value.

```python
with open("input/sales.csv", "r") as f:
    reader = csv.DictReader(f)
    print(reader.fieldnames)   # column headers as list
    for row in reader:
        print(row["region"])   # access by column name
```

`reader.fieldnames` only works inside the `with` block — inspect schema before closing file.

---

## 2. Schema Inspection

Always inspect before processing. Never parse blind data.

```python
with open("input/sales.csv", "r") as f:
    reader = csv.DictReader(f)
    print(reader.fieldnames)   # columns
    count = 0
    for row in reader:
        if count == 5:
            break
        print(row)
        count += 1
```

---

## 3. Cleaning vs Validation — Key Distinction

| | Cleaning | Validation |
|---|---|---|
| Goal | Normalize messy data | Detect broken/invalid data |
| Action | Fix it | Flag and reject it |
| Example | `" north "` → `"North"` | `"-2"` as region → reject row |

Both happen in one pass over the data — cleaning first, then validation.

---

## 4. Cleaning Techniques

### Strip whitespace + standardize casing
```python
row["region"] = row["region"].strip().title()
# " north " → "North"
# "SOUTH"   → "South"
```

`.strip().title()` — use on any text field that comes from raw input.

### Detect missing values
```python
if row["product"] == "":
    is_valid = False
```

`csv.DictReader` returns empty string `""` for missing fields — not `None`.

---

## 5. Validation Techniques

### is_valid flag pattern
```python
is_valid = True

# run all checks — set False on any failure
if row["date"] == "":
    is_valid = False

if row["region"] not in valid_regions:
    is_valid = False

# only append if all checks passed
if is_valid:
    cleaned_rows.append(row)
```

Single flag per row — all checks run, row rejected if any fail.

### Whitelist validation
```python
valid_regions = ["North", "South", "East", "West"]

if row["region"] not in valid_regions:
    print(f"Invalid region: {row['region']}")
    is_valid = False
```

Define allowed values explicitly — reject anything outside the list.

### Duplicate detection with set()
```python
seen_order_ids = set()

if row["order_id"] in seen_order_ids:
    is_valid = False
else:
    seen_order_ids.add(row["order_id"])
```

`set()` lookup is faster than checking a list. Use for ID deduplication.

### Date format validation
```python
if row["date"] == "":
    is_valid = False
else:
    try:
        datetime.strptime(row["date"], "%Y-%m-%d")
    except ValueError:
        is_valid = False
```

Check missing first, then validate format — avoids running `strptime` on empty string.

`datetime.strptime(string, format)` — raises `ValueError` if format doesn't match.

### Type conversion with try/except
```python
try:
    row["quantity"] = int(row["quantity"])
    row["unit_price"] = float(row["unit_price"])
    row["total"] = float(row["total"])
except ValueError:
    is_valid = False
```

All CSV values are strings by default — must convert before doing math. If conversion fails, row is invalid.

---

## 6. Filtering

```python
filtered_rows = []
for row in cleaned_rows:
    if row["status"] == "Completed" and row["total"] > 100:
        filtered_rows.append(row)
```

- `==` for exact field match (status, region, category)
- `>` / `<` for numeric range (total, quantity)
- `and` / `or` for multi-condition

Works on `cleaned_rows` — always filter after cleaning, never on raw data.

---

## 7. Sorting with lambda

```python
sorted_rows = sorted(
    filtered_rows,
    key=lambda row: row["total"],
    reverse=True   # descending
)
```

`lambda row: row["total"]` — anonymous function that returns the sort key.
`reverse=True` → highest first. `reverse=False` (default) → lowest first.

For dates (string format `YYYY-MM-DD`), string sort = chronological sort — works without `datetime` conversion.

```python
sorted_rows = sorted(rows, key=lambda row: row["date"])
```

### max() and min() with lambda
```python
highest = max(cleaned_rows, key=lambda row: row["total"])
lowest  = min(cleaned_rows, key=lambda row: row["total"])
```

Same `key=` pattern as `sorted()`.

---

## 8. Analytics

### Sum
```python
total_rev = 0
for row in cleaned_rows:
    total_rev += row["total"]

total_rev = round(total_rev, 2)   # float precision fix
```

### Average
```python
average = round(total_rev / len(cleaned_rows), 2)
```

Always `round()` float results — raw float math produces ugly decimals.

### Grouping — revenue per category
```python
category_rev = {}
for row in cleaned_rows:
    category = row["category"]
    if category in category_rev:
        category_rev[category] += row["total"]
    else:
        category_rev[category] = row["total"]
```

Same frequency counter pattern from TXT parsing — here accumulating values instead of counts.

### Frequency counter — count per region
```python
region_counts = {}
for row in cleaned_rows:
    region = row["region"]
    if region in region_counts:
        region_counts[region] += 1
    else:
        region_counts[region] = 1
```

---

## 9. csv.DictWriter — Export

```python
with open("output/cleaned.csv", "w", newline="") as f:
    fieldnames = ["order_id", "date", "customer", ...]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()     # writes column headers
    writer.writerows(rows)   # writes all rows at once
```

`newline=""` — required to prevent blank rows between entries on Windows.
`fieldnames` must be defined explicitly — controls column order in output.

---
