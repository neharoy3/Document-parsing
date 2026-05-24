import csv
from datetime import datetime
import json

# 1)Schema inspection

with open("input/sales_dirty.csv","r") as f:
    reader = csv.DictReader(f)
    print("\nColumns:\n")
    print(reader.fieldnames)
    print("\nFirst 5 Rows:\n")
    count = 0
    for row in reader:
        if count == 5:
            break
        print(row)
        count += 1


# 2)Cleaning data

cleaned_rows = []
valid_regions = ["North", "South", "East", "West"]
seen_order_ids = set()

with open("input/sales_dirty.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        is_valid = True

        #remove whitespace, standardize casing
        row["customer"] = row["customer"].strip().title()
        row["product"] = row["product"].strip().title()
        row["region"] = row["region"].strip().title()
        row["category"] = row["category"].strip().title()
        row["status"] = row["status"].strip().title()


        #missing values
        if row["product"] == "":
            print(f"Missing product found -> Order ID: {row['order_id']}")
            is_valid = False

        if row["category"] == "":
            print(f"Missing category found -> Order ID: {row['order_id']}")
            is_valid = False

        #duplicates
        if row["order_id"] in seen_order_ids:
            print(f"Duplicate Order ID found: {row['order_id']}")
            is_valid = False
        else:
            seen_order_ids.add(row["order_id"])

        #region validation
        if row["region"] not in valid_regions:
            print(f"Invalid region found: {row['region']}")
            is_valid = False

        #date validation
        if row["date"] == "":
            print(f"Missing date -> Order ID: {row['order_id']}")
            is_valid = False
        else: # only validate format if date exists
            try:
                datetime.strptime(row["date"], "%Y-%m-%d")
            except ValueError:
                print(f"Invalid date: {row['date']}")
                is_valid = False

        #convert data types
        try:
            row["quantity"] = int(row["quantity"])
            row["unit_price"] = float(row["unit_price"])
            row["total"] = float(row["total"])
        except ValueError:
            print(f"Invalid numeric value -> Order ID: {row['order_id']}")
            is_valid = False

        if is_valid:
            cleaned_rows.append(row)


# 3)Export cleaned data

with open("output/sales_cleaned.csv", "w", newline="") as f:
    fieldnames = [
        "order_id",
        "date",
        "customer",
        "region",
        "product",
        "category",
        "quantity",
        "unit_price",
        "total",
        "status"
    ]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(cleaned_rows)

print("\nCleaned CSV exported.")

# 3)Filtering data

filtered_rows = []
for row in cleaned_rows:
    if row["status"] == "Completed" and row["total"] > 100:
        filtered_rows.append(row)
print("\nHigh Value Completed Orders:\n")
for row in filtered_rows:
    print(row)

# 4)Export filtered data
with open("output/high_value_sales.csv", "w", newline="") as f:
    fieldnames = [
        "order_id",
        "date",
        "customer",
        "region",
        "product",
        "category",
        "quantity",
        "unit_price",
        "total",
        "status"
    ]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(filtered_rows)

print("\nFiltered CSV exported.")
print("--------------------------------------------------------------------")

# 5)Sorting data
sorted_rows = sorted(
    filtered_rows,
    key=lambda row: row["total"],
    reverse=True
)

print("\nTop 5 Highest Sales:\n")
for row in sorted_rows[:5]:
    print(row)
print("--------------------------------------------------------------------")

# 6)Export sorted data
with open("output/sorted_sales.csv", "w", newline="") as f:
    fieldnames = [
        "order_id",
        "date",
        "customer",
        "region",
        "product",
        "category",
        "quantity",
        "unit_price",
        "total",
        "status"
    ]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(sorted_rows)
print("\nSorted CSV exported.")
print("--------------------------------------------------------------------")

print("\nAnalysis:\n")

total_rev = 0
for row in cleaned_rows:
    total_rev+=row["total"]
print(f"\nTotal Revenue: {round(total_rev, 2)}")
print("--------------------------------------------------------------------")

average_ord = total_rev / len(cleaned_rows)
print(f"\nAverage Order Value: {round(average_ord,2)}")
print("--------------------------------------------------------------------")

highest_ord = max(cleaned_rows, key=lambda row: row["total"])
lowest_ord = min(cleaned_rows, key=lambda row: row["total"])
print("\nHighest Order:\n")
print(highest_ord)
print("\nLowest Order:\n")
print(lowest_ord)
print("--------------------------------------------------------------------")

region_counts = {}
for row in cleaned_rows:
    region = row["region"]
    if region in region_counts:
        region_counts[region] += 1
    else:
        region_counts[region] = 1
print("\nSales Count Per Region:\n")
for region, count in region_counts.items():
    print(f"{region}: {count}")
print("--------------------------------------------------------------------")

category_rev = {}
for row in cleaned_rows:
    category = row["category"]
    if category in category_rev:
        category_rev[category] += row["total"]
    else:
        category_rev[category] = row["total"]
print("\nRevenue Per Category:\n")
for category, revenue in category_rev.items():
    print(f"{category}: {revenue}")
print("--------------------------------------------------------------------")

# Export data to json
analytics = {
    "total_revenue": total_rev,
    "average_order_value": average_ord,
    "highest_order": highest_ord,
    "lowest_order": lowest_ord,
    "sales_per_region": region_counts,
    "revenue_per_category": category_rev
}

with open("output/analytics_summary.json", "w") as f:
    json.dump(analytics, f, indent=4)
print("\nAnalytics JSON exported.")