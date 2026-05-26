import pdfplumber
import re
import csv
import json

all_text = []
with pdfplumber.open("input/sample.pdf") as pdf:
    print(f"Total pages: {len(pdf.pages)}\n")
    print(f"Metadata:\n{pdf.metadata}")
    
    print("--------------------------------------------------------------------")

    for i, page in enumerate(pdf.pages):  #returns index and obj

        #page extraction
        print(f"Extracting page {i + 1}") #progress tracking
        #text extraction
        text = page.extract_text(layout=True) #preserve spatial layout

        #ocr detection
        if not text:
            print(f"Page {i + 1} may be scanned/image-based")
        #cleaning
        if text:
            text = text.replace("\n\n","\n") #normalize spacing
            text = "\n".join(line.strip() for line in text.splitlines()) #line by line cleaning
            all_text.append(text)

document_text = "\n".join(all_text)
print("\nFinal Extracted Text:\n")
print(document_text[:1000])

print("--------------------------------------------------------------------")

# page-level chunking
page_chunks = [
    {
        "page": i + 1,
        "text": text
    }
    for i, text in enumerate(all_text)
]
print("\nPage Chunks:\n")
for chunk in page_chunks[:3]:
    print(f"\n--- Page {chunk['page']} ---\n")
    print(chunk["text"][:500])
    
print("--------------------------------------------------------------------")

#extract captured content
abstract_match = re.search(r"Abstract(.*?)Introduction", document_text, re.DOTALL)
if abstract_match:
    abstract = abstract_match.group(1).strip()
    print("\nABSTRACT:\n")
    print(abstract[:1000])

print("--------------------------------------------------------------------")

#heading detection
headings = re.findall(r"\n([A-Z][A-Za-z0-9\s\-]{2,50})\n",document_text)
#starts with uppercase, letters/nums/spaces/hyphens, length
print("\nDetected Headings:\n")
for heading in headings[:20]:
    print(heading)

print("--------------------------------------------------------------------")

pattern = r"\n([A-Z][A-Za-z0-9\s\-]{2,50})\n"
matches = list(re.finditer(pattern, document_text)) #iterable match objs
sections = []

for i in range(len(matches)):
    heading = matches[i].group(1).strip()
    start = matches[i].end() #section start
    if i+1 < len(matches):
        end = matches[i+1].start() #section end
    else:
        end = len(document_text)
    content = document_text[start:end].strip()
    sections.append({
        "heading":heading,
        "content":content
    })

print("\nSection chunks:\n")
for section in sections[:5]:
    print(f"\n=== {section['heading']} ===\n")
    print(section["content"][:500])

print("--------------------------------------------------------------------")

#table extraction

all_tables = []
with pdfplumber.open("input/sample.pdf") as pdf:
    for page_num, page in enumerate(pdf.pages, start = 1):
        tables = page.extract_tables()
        if tables:
            for table in tables:
                print(f"\nTable found on page {page_num}\n")
                headers = table[0] #column names
                structured_rows = []
                for row in table[1:]:
                    if row and len(row) == len(headers):
                        cleaned_row = []
                        for cell in row:
                            if cell:
                                cell = " ".join(cell.split())
                            else:
                                cell = ""
                            cleaned_row.append(cell)

                        row_dict = dict(zip(headers, cleaned_row))

                        if row_dict not in structured_rows:
                            structured_rows.append(row_dict)

                all_tables.extend(structured_rows)
                for row in structured_rows:
                    print(row)

print("--------------------------------------------------------------------")

#export to json and csv

with open("output/sections.json","w") as f:
    json.dump(sections, f, indent = 4)
print("Sections exported to JSON.")

if all_tables:
    with open("output/tables.csv","w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=all_tables[0].keys())
        writer.writeheader()
        writer.writerows(all_tables)
    print("\nTables exported to CSV.")

print("--------------------------------------------------------------------")

# layout analysis

with pdfplumber.open("input/sample.pdf") as pdf:
    first_page = pdf.pages[0]
    words = first_page.extract_words()
    print("\nWord layout data:\n")
    for word in words[:10]:
        print(word)
