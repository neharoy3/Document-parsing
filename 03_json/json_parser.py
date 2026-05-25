import json
from datetime import datetime

# Read JSON + schema inspection
with open("input/orders_dirty.json","r") as f:
    data = json.load(f)

print(data.keys()) #top level keys
print(type(data))  #dict in python
print(type(data["orders"])) #list
print(f"First order: {data['orders'][0]}\n")
print("--------------------------------------------------------------------")

# nested hierarchy
print(f"First customer name: {data['orders'][0]['customer']['name']}\n")
print(f"First customer city: {data['orders'][0]['customer']['address']['city']}\n")
print(f"First item name: {data['orders'][0]['items'][0]['name']}\n")

print("Order ids:\n")
for order in data["orders"]:
    print(order["order_id"])
    
print("\nItem names:\n")
for order in data["orders"]:
    for item in order["items"]:
        print(item["name"])
print("--------------------------------------------------------------------")

# safe access with .get() to handle missing data
print("\nCustomer emails:\n")
for order in data["orders"]:
    email = order["customer"].get("email", "No email")
    # .get() prevents crashes if key is missing
    print(email) 

print("\nShipping carrier:\n")
for order in data["orders"]:
    shipping = order.get("shipping")
    if shipping:
        print(shipping.get("carrier"))

# cleaning + validation
cleaned_orders = []
for order in data["orders"]:
    is_valid = True #validation flag
    order["customer"]["name"] = (order["customer"]["name"]).strip().title() #clean names
    order["status"] = order["status"].title() #status casing

    #email
    email = order["customer"].get("email","") 
    if "@" not in email:
        print(f"Invalid email -> {order['order_id']}")
        is_valid = False
        
    #empty items
    if len(order["items"]) == 0:
        print(f"Empty items list -> {order['order_id']}")
        is_valid = False

    #negative quantity
    for item in order["items"]:
        if item["quantity"] <0:
            print(f"Negative quantity -> {order['order_id']}")
            is_valid = False

    try:
        datetime.strptime(
            order["placed_at"],
            "%Y-%m-%dT%H:%M:%SZ"
        )
    except ValueError:
        print(f"Invalid datetime -> {order['order_id']}")
        is_valid = False

    if is_valid:
        cleaned_orders.append(order)
print("--------------------------------------------------------------------")
    
# filtering + extraction
completed_orders = []
high_value_orders = []
customer_names = []
cities = []
products = []

for order in cleaned_orders:
    if order["status"] == "Completed":
        completed_orders.append(order)

    if order["payment"]["amount"] > 300:
        high_value_orders.append(order) 
        
    customer_names.append(order["customer"]["name"])

    address = order["customer"].get("address")
    if address:
        cities.append(address.get("city"))
    
    for item in order["items"]:
        products.append(item["name"])

#print stuff
'''
print("Customer names:\n\n",customer_names)
print("--------------------------------------------------------------------")
print("Products:\n\n",products)
print("--------------------------------------------------------------------")

print("\nCompleted Orders:\n")
for order in completed_orders:
    print(order["order_id"])

print("--------------------------------------------------------------------")
print("High value orders:\n\n",high_value_orders)
print("--------------------------------------------------------------------")
print("Cities:\n\n",cities)
print("--------------------------------------------------------------------")
'''

## IMP: Flattening: tabular-friendly structure

flattened_orders = []
for order in cleaned_orders:
    address = order["customer"].get("address")
    city = "Unknown"
    if address:
        city = address.get("city", "Unknown")

    # flattened structure
    flat_order = {
        "order_id": order["order_id"],
        "customer_name": order["customer"]["name"],
        "city": city,
        "status": order["status"],
        "payment_amount": order["payment"]["amount"]
    }
    flattened_orders.append(flat_order)

print("\nFlattened Orders:\n")
for order in flattened_orders:
    print(order)

# Export JSON
with open("output/orders_cleaned.json","w") as f:
    json.dump(cleaned_orders, f, indent = 4)
print("\nCleaned orders exported.")

with open("output/completed_orders.json", "w") as f:
    json.dump(completed_orders, f, indent = 4)
print("\nCompleted orders exported.")

with open("output/high_value_orders.json", "w") as f:
    json.dump(high_value_orders, f, indent = 4)
print("\nHigh value orders exported.")

with open("output/flattened_orders.json", "w") as f:
    json.dump(flattened_orders, f, indent = 4)
print("\nFlattened orders exported.")