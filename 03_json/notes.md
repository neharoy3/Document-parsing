# JSON Parsing — Core Concepts
> reading · nested access · cleaning · validation · filtering · flattening · export

---

## JSON Processing Pipeline

```text
 Read
   ↓
Inspect
   ↓
Traverse
   ↓
 Clean
   ↓
Validate
   ↓
 Extract
   ↓
 Flatten
   ↓
 Export
```

Structured JSON parsing is usually done in stages instead of processing everything at once.

---

## 1. Reading JSON

```python
import json

with open("input/orders.json", "r") as f:
    data = json.load(f)
```

`json.load()` reads JSON from an opened file object.

`json.loads()` reads JSON from a string.

```python
json_string = '{"name": "Alice", "age": 25}'
data = json.loads(json_string)
```

Used when receiving:
- API responses
- OCR output
- AI-generated JSON
- raw JSON strings

Result becomes native Python types:
- dict
- list
- str
- int / float
- bool
- `None`

---

## 2. Schema Inspection

Always inspect structure before writing processing logic.

```python
print(data.keys())
print(type(data))
print(type(data["orders"]))
print(data["orders"][0])
```

Questions to answer first:
- Is root object a dict or list?
- What fields exist?
- Which fields are nested?
- Which fields contain lists?
- Which fields can be null?

JSON structures may be:
- flat dict

```python
{"name": "Alice"}
```

- list of dicts

```python
[{"name": "Alice"}, {"name": "Bob"}]
```

- deeply nested

```python
{
    "customer": {
        "address": {
            "city": "Austin"
        }
    }
}
```

Understanding nesting depth first prevents traversal mistakes later.

---

## 3. Nested Access

### Nested dict access

```python
data["orders"][0]["customer"]["name"]
data["orders"][0]["customer"]["address"]["city"]
```

Each `["key"]` moves one level deeper into the structure.

---

### Nested list traversal

```python
for order in data["orders"]:
    for item in order["items"]:
        print(item["name"])
```

Nested lists usually require nested loops when processing all values.

Mental model:

```text
dict
 └── list
      └── dict
           └── dict
```

Most JSON parsing complexity comes from navigating nested structures correctly.

---

## 4. Safe Access with `.get()`

```python
dict["key"]
```

Raises:

```python
KeyError
```

if key does not exist.

---

### Safe access

```python
email = order["customer"].get("email", "No email")
```

Behavior:
- key exists → returns value
- key missing → returns default

`.get()` prevents crashes when fields are optional.

---

## JSON null vs Python None

JSON:

```json
"address": null
```

becomes:

```python
None
```

in Python.

---

### Null-safe nested access

```python
shipping = order.get("shipping")
if shipping:
    print(shipping.get("carrier"))
```

Pattern:
1. get object
2. check if object exists
3. access nested fields

---

### Safe nested access pattern

```python
address = order["customer"].get("address")
city = "Unknown"
if address:
    city = address.get("city", "Unknown")
```

`.get(default)` only protects against:
- missing keys

It does NOT protect against:
- existing keys with value `None`

---

### When to use `.get()`

Use:

```python
dict["key"]
```

for guaranteed fields.

Use:

```python
.get()
```

for:
- optional fields
- nullable fields
- inconsistent JSON

---

## 5. Cleaning

### Strip whitespace + standardize casing

```python
order["customer"]["name"] = (
    order["customer"]["name"]
    .strip()
    .title()
)

order["status"] = order["status"].title()
```

Same cleaning concepts from CSV parsing apply to nested JSON values too.

Typical cleaning:
- `.strip()`
- `.lower()`
- `.upper()`
- `.title()`

---

## 6. Validation

Validation checks whether data is structurally and logically correct.

Use validation flag pattern:

```python
is_valid = True
# checks...
if is_valid:
    cleaned_orders.append(order)
```

Runs all checks before rejecting record.

---

### Email validation

```python
email = order["customer"].get("email", "")
if "@" not in email:
    is_valid = False
```

Basic substring validation for malformed email values.

---

### Empty nested list validation

```python
if len(order["items"]) == 0:
    is_valid = False
```

Avoids processing orders with no items.

---

### Negative value validation

```python
for item in order["items"]:
    if item["quantity"] < 0:
        is_valid = False
```

Validation can happen inside nested structures too.

---

### Datetime validation

```python
from datetime import datetime

try:
    datetime.strptime(
        order["placed_at"],
        "%Y-%m-%dT%H:%M:%SZ"
    )
except ValueError:
    is_valid = False
```

ISO 8601 format:

```text
2024-01-05T08:23:11Z
```

Malformed timestamps raise:

```python
ValueError
```

Examples:
- missing time
- incorrect separators
- wrong format

---

## 7. Filtering + Extraction

```python
completed_orders = []
cities = []
products = []

for order in cleaned_orders:
    if order["status"] == "Completed":
        completed_orders.append(order)
    address = order["customer"].get("address")
    if address:
        cities.append(address.get("city"))
    for item in order["items"]:
        products.append(item["name"])
```

Filtering:
- selects matching records

Extraction:
- pulls specific values from structure

Extraction from nested lists requires additional traversal loops.

---

## 8. Flattening

Flattening converts nested JSON into flat tabular-friendly structures.  
It is often required before exporting nested JSON into CSV or analytics tools.

Example:

```python
flat_order = {
    "order_id": order["order_id"],
    "customer_name": order["customer"]["name"],
    "city": city,
    "status": order["status"],
    "payment_amount": order["payment"]["amount"]
}
```

Flattening:
- surfaces important nested fields
- removes deep hierarchy
- prepares data for CSV/export/analytics

Use descriptive field names:
- `customer_name`
- `payment_amount`

instead of generic names like:
- `name`
- `amount`

---

### Handle nulls before flattening

```python
address = order["customer"].get("address")
city = "Unknown"
if address:
    city = address.get("city", "Unknown")
```

Always safely resolve optional nested fields before flattening.

---

## 9. Exporting JSON

```python
with open("output/cleaned.json", "w") as f:
    json.dump(data, f, indent=4)
```

`json.dump()` writes Python objects into JSON files.

---

### `indent=4`

```python
json.dump(data, f, indent=4)
```

Creates human-readable formatted JSON.
Without indentation everything becomes one giant line.

---

### `json.dumps()`

```python
json_string = json.dumps(data, indent=4)
```

Returns JSON as a string instead of writing to file.

Useful for:
- APIs
- logging
- debugging
- printing formatted JSON

---

## 10. JSON vs CSV — Key Difference

| | JSON | CSV |
|---|---|---|
| Structure | Nested, hierarchical | Flat, tabular |
| Missing values | `null` / missing key | Empty string `""` |
| Nested data | Native support | Must flatten first |
| Access style | `dict["key"]` / `.get()` | `row["column"]` |
| Python structure | dict / list | dict (via DictReader) |

- JSON parsing typically involves deeper traversal, null handling, and hierarchical extraction compared to CSV parsing.