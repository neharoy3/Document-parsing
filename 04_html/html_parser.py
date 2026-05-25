import requests
from bs4 import BeautifulSoup
import csv
import json

with open("input/products.html","r") as f:
    html = f.read()

#Parse and inspection
soup = BeautifulSoup(html, "html.parser")
# print(type(soup))
print(f"\nTitle:\n{soup.title}")
# print(f"\nFormatted HTML Structure:\n{soup.prettify()[:3000]}")
print(f"\nFirst h1:\n{soup.find('h1')}")

print("\nAll links:\n")
links = soup.find_all("a")
for link in links:
    print(link.get("href"))

print("\nFirst product card:\n")
product = soup.find("div", class_="product-card")
print(product)

print("\nFeatured products:\n")
featured_p = soup.find_all("div", class_="product-card featured")
for product in featured_p:
    print(product.get("id"))

print("\nElement by ID:\n")
main_table = soup.find(id = "product-table")
print(main_table)

#Data extraction
print("\nProduct names:\n")
product_cards = soup.find_all("div", class_="product-card")
for card in product_cards:
    name = card.find("h3", class_ = "product-name")
    if name:
        print(name.text.strip())

print("\nPrices:\n")
for card in product_cards:
    price = card.find("span", class_="price")
    if price:
        print(price.text.strip())
       
print("\nProduct Links:\n")
for card in product_cards:
    link = card.find("a", class_="product-link")
    if link:
        print(link.get("href"))

print("--------------------------------------------------------------------")

# Cleaning + validation
print("\nCleaned products:\n")
cleaned_p = []
for card in product_cards:
    is_valid = True

    #product name
    name_tag = card.find("h3", class_ = "product-name")
    if name_tag:
        name = name_tag.text.strip()
    else:
        print("Missing product name")
        is_valid = False
    
    #price
    price_tag = card.find("span", class_="price")
    if price_tag:
        price = price_tag.text.strip()
        price = "".join(price.split())
    else:
        print(f"Missing price tag -> {name}")
        is_valid = False

    #empty price validation
    if price == "":
        print(f"Empty price -> {name}")
        is_valid = False

    #product link
    link_tag = card.find("a", class_="product-link")
    href = None
    if link_tag:
        href = link_tag.get("href")
    if not href:
        print(f"Missing href -> {name}")
        is_valid = False

    #description
    desc_tag = card.find("p", class_="description")
    desc = ""
    if desc_tag:
        desc = desc_tag.text.strip()
    #empty desc
    if desc=="":
        print(f"Empty description -> {name}")
    if is_valid:
        cleaned_p.append({
            "name": name,
            "price": price,
            "description": desc,
            "url": href
        })
print("\nValid products:\n")
for product in cleaned_p:
    print(product)

print("--------------------------------------------------------------------")

#Filtering + flattening

print("\nFeatured Products:\n")
featured_products = []
for card in product_cards:
    classes = card.get("class", [])
    if "featured" in classes:
        name_tag = card.find("h3", class_="product-name")
        if name_tag:
            print(name_tag.text.strip())
            featured_products.append(name_tag.text.strip())
print("\nStructured Product Data:\n")

structured_p = []
for card in product_cards:
    is_valid = True

    #name
    name_tag = card.find("h3", class_="product-name")
    if name_tag:
        name = name_tag.text.strip()
    else:
        is_valid = False

    #price
    price_tag = card.find("span", class_="price")
    if price_tag:
        price = price_tag.text.strip()
        price = "".join(price.split())
    else:
        is_valid = False
    if price == "":
        is_valid = False

    #category
    category_tag = card.find("span", class_="category")
    category = ""
    if category_tag:
        category = category_tag.text.strip()

    #stock
    stock_tag = card.find("span", class_="stock")
    stock = ""
    if stock_tag:
        stock = stock_tag.text.strip()

    #rating
    rating_tag = card.find("span", class_="rating")
    rating = ""
    if rating_tag:
        rating = rating_tag.text.strip()

    #link
    link_tag = card.find("a", class_="product-link")
    href = None
    if link_tag:
        href = link_tag.get("href")
    if not href:
        is_valid = False
    if is_valid:

        structured_p.append({

            "name": name,

            "category": category,

            "price": price,

            "stock": stock,

            "rating": rating,

            "url": href
        })

for product in structured_p:
    print(product)

print("--------------------------------------------------------------------")

# Parent + child traversal
print("\nParent of Product Card:")
product = soup.find("div", class_="product-card")
print(product.parent.name)

print("\nChildren of Product Card:")
for child in product.children:
    if child.name:
        print(child.name)

print("--------------------------------------------------------------------")

# HTML table parsing: tr=table row, td=table cell
print("\nTable Data:\n")
table = soup.find("table", id="product-table")
rows = table.find_all("tr")
table_products = []

for row in rows[1:]:
    cells = row.find_all("td")
    product = {
        "name": cells[0].text.strip(),
        "category": cells[1].text.strip(),
        "price": cells[2].text.strip(),
        "rating": cells[3].text.strip(),
        "stock": cells[4].text.strip()
    }
    table_products.append(product)

for product in table_products:
    print(product)

print("--------------------------------------------------------------------")

# CSS selector: 

print("select():\n") #equivalent to find_all()
products = soup.select(".product-card")
for product in products:
    print(product.get("id"))

print("\nselect_one():") ##equivalent to find()
product = soup.select_one(".product-card")
print(product.get("id"))
print("--------------------------------------------------------------------")

#Export to csv and json
with open("output/products_cleaned.json","w") as f:
    json.dump(structured_p, f, indent = 4)
print("JSON exported.")

with open("output/products_cleaned.csv","w") as f:
    fieldnames = [
        "name",
        "category",
        "price",
        "stock",
        "rating",
        "url"
    ]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(structured_p)
print("CSV exported.")

print("--------------------------------------------------------------------")

# Fetching live HTML

url = "https://books.toscrape.com/"
response = requests.get(url)
print(response.status_code)
html = response.text
soup = BeautifulSoup(html, "html.parser")
print(soup.title.text.strip())
