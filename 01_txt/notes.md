# TXT Parsing — Core Concepts
> keyword search · error counter · data extraction · structured parsing · export

---

## 1. Opening Files

Always use `with open()` — auto-closes file, no `f.close()` needed.

```python
with open("logs.txt", "r") as f:
    ...
```

### Modes
| Mode | Behaviour |
|------|-----------|
| `"r"` | Read. Fails if file doesn't exist. |
| `"w"` | Write. Creates file or **overwrites** existing. |
| `"a"` | Append. Creates file or adds to end. |

---

## 2. read() vs readlines()

| | `f.read()` | `f.readlines()` |
|---|---|---|
| Returns | One big string | List of lines |
| Use when | Running regex on full text | Processing line by line |

```python
f.read()       # → "2024-01-01 ERROR crash\n2024-01-02 INFO ok\n"
f.readlines()  # → ["2024-01-01 ERROR crash\n", "2024-01-02 INFO ok\n"]
```

> **Rule:** regex on full file → `read()`. looping over lines → `readlines()`.

---

## 3. String Matching

### Exact vs Substring
```python
"error" == "database error"   # False — exact, useless for search
"error" in "database error"   # True  — substring match
```

### When to use which
```python
# searching anywhere in a line → in + .lower()
if "error" in line.lower():

# extracting a known column → split() + ==
parts = line.split()
level = parts[2]       # "2024-01-01 08:00:00 ERROR message"
if level == "ERROR":   #  index: 0          1     2
```

> `split()` breaks line on whitespace → `parts[2]` is always the log level if format is fixed.
> `==` is correct here — field is already isolated, no substring search needed.

### Case-insensitive matching
```python
"error" in line.lower()   # catches ERROR, Error, error
```
Use `.lower()` when searching full line. Not needed when using `split()` + exact field.

### strip() — remove \n and spaces
```python
line.strip()    # both sides — use before printing or storing
line.rstrip()   # right side only — useful for lines with trailing \n
```
Forgetting `.strip()` = `\n` sneaks into output. Common bug.

---

## 4. Counting with Dictionaries

Manual frequency counter pattern:
```python
counts = {}
for item in items:
    if item in counts:
        counts[item] += 1
    else:
        counts[item] = 1
```

Loop over results:
```python
for key, value in counts.items():
    print(f"{key} → {value}")
```

Use when: counting IPs, log levels, usernames — anything that repeats.

---

## 5. Deduplication with set()

```python
users = ["Rahul", "Priya", "Rahul"]
set(users)          # {"Rahul", "Priya"} — removes duplicates
sorted(set(users))  # sorted too, if order matters
```

Use `set()` before printing or writing — avoids duplicate entries in output.

---

## 6. Regex

### Import
```python
import re
```

### Symbols:
```
.       - Any Character Except New Line  
\d      - Digit (0-9)  
\D      - Not a Digit (0-9)  
\w      - Word Character (a-z, A-Z, 0-9, _)  
\W      - Not a Word Character  
\s      - Whitespace (space, tab, newline)  
\S      - Not Whitespace (space, tab, newline)  

\b      - Word Boundary  
\B      - Not a Word Boundary  
^       - Beginning of a String  
$       - End of a String  

[]      - Matches Characters in brackets  
[^ ]    - Matches Characters NOT in brackets  
|       - Either Or  
( )     - Group  

*       - 0 or More  
+       - 1 or More  
?       - 0 or One  
{3}     - Exact Number  
{3,4}   - Range of Numbers (Minimum, Maximum)  
```
---

### re.findall() — extract all matches from full text

```python
ips = re.findall(r"\d+\.\d+\.\d+\.\d+", text)
# → ["192.168.1.1", "10.0.0.5", "192.168.1.1"]
```

Returns list. Use on `f.read()` output (full string).

---

### re.match() — match from start of line

```python
m = re.match(r"(\d{4}-\d{2}-\d{2}) (\w+) (.*)", line)
if m:
    date = m.group(1)
```

Returns match object or `None`. Always check `if m:` before using `.group()`.
Use on individual lines from `f.readlines()`.

---

### Capturing Groups

`( )` extracts specific part of a match.

```python
# Without group — returns full match
re.findall(r"User \w+", text)    # ["User Rahul", "User Priya"]

# With group — returns only captured part
re.findall(r"User (\w+)", text)  # ["Rahul", "Priya"]
```

Multiple groups with `re.match()`:
```python
m = re.match(r"(\d{4}-\d{2}-\d{2}) (INFO|ERROR|WARNING) (.*)", line)
m.group(1)  # date
m.group(2)  # level
m.group(3)  # message
# group(0) = full match always
```

---

### OR in regex

```python
r"INFO|ERROR|WARNING"           # matches any of the three
r"Failed login.*|Unauthorized access.*"  # matches either phrase + anything after
```

---

### Useful patterns from this exercise

```python
IP        = r"\d+\.\d+\.\d+\.\d+"
TIMESTAMP = r"\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}"
USERNAME  = r"User (\w+)"
LOG_LINE  = r"(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2}) (INFO|ERROR|WARNING) (.*)"
```

---

## 7. Structured Parsing

Goal: convert raw log line → Python dictionary.

```python
all_logs = []

for line in lines:
    m = re.match(LOG_PATTERN, line)
    if m:
        all_logs.append({
            "date":    m.group(1),
            "time":    m.group(2),
            "level":   m.group(3),
            "message": m.group(4).strip()
        })
```

Result: list of clean dicts, easy to export anywhere.

```
Raw line: "2024-01-15 08:23:11 ERROR Failed login for User Rahul"
    ↓
Dict: {"date": "2024-01-15", "time": "08:23:11", "level": "ERROR", "message": "Failed login for User Rahul"}
```

---

## 8. Exporting Data

### TXT — raw write
```python
with open("output.txt", "w") as f:
    for item in data:
        f.write(item + "\n")   # write() doesn't add \n automatically
```

### JSON — structured, readable, API-friendly
```python
import json
with open("output.json", "w") as f:
    json.dump(data, f, indent=4)
```

### CSV — tabular, opens in Excel
```python
import csv
with open("output.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["date", "time", "level", "message"])
    writer.writeheader()
    writer.writerows(data)
```

| Format | Best for |
|--------|----------|
| TXT | Human-readable logs, simple output |
| JSON | Structured data, APIs, further processing |
| CSV | Analytics, spreadsheets, tabular data |

---

## 9. Full Parsing Flow

```
Open file
    ↓
read() or readlines() depending on task
    ↓
Search / extract with regex OR match with string ops
    ↓
Store in list / dict
    ↓
Export → TXT / JSON / CSV
```

---
