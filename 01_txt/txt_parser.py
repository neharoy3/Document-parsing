import re
import json
import csv

'''
1)Keyword search:
'''

keyword = input("Enter the keyword to search: ")
with open("input/logs.txt","r") as f:
    logs = f.readlines()

count = 0
print("\nMatching logs: \n")

for line in logs:
    if keyword.lower() in line.lower():
        print(line.strip())
        count +=1
    
if count>0:
    print(f"\nTotal matches found: {count}")
else:
    print("No matching logs found")

print("--------------------------------------------------------------------")
'''
2) Error Counter:

INFO: X
WARNING: X
ERROR: X

'''

info_count = 0
warning_count = 0
error_count = 0

with open("input/logs.txt","r") as f:
    lines = f.readlines()

for line in lines:
    parts = line.split()
    level = parts[2]
    if level == "INFO":
        info_count += 1
    elif level == "ERROR":
        error_count += 1
    elif level == "WARNING":
        warning_count += 1
        
print("\nError counter:\n")
print(f"INFO: {info_count}\nWARNING: {warning_count}\nERROR: {error_count}")

print("--------------------------------------------------------------------")
'''
3)Data Extractor:

'''
with open("input/logs.txt","r") as f:
    lines = f.read()

# IPs
ips = re.findall(r"\d+\.\d+\.\d+\.\d+", lines)
print("\nAll IP matches: \n")
for i in ips:
    print(i)

ip_count={}
for i in ips:
    if i in ip_count:
        ip_count[i]+=1
    else:
        ip_count[i]=1
    
print("\nIP Counts:\n")
for ip, count in ip_count.items():
    print(f"IP: {ip} -> Count: {count}")
print("--------------------------------------------------------------------")

# Usernames
users = re.findall(r"User (\w+)", lines)
print("\nUsernames:\n")

for u in set(users):
    print(u)

print("--------------------------------------------------------------------")

# Timestamp
print("\nTimestamps:\n")
times = re.findall(r"\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}",lines)
for t in sorted(set(times)):
    print(t)
print("--------------------------------------------------------------------")

# Failed logins
print("\nFailed Logins Detected:\n")
failed = re.findall(r"ERROR (Failed login.*|Unauthorized access.*)",lines)
for entry in set(failed):
    print(entry)
print("--------------------------------------------------------------------")

'''
4) Data Extraction
'''

# Export extracted IPs to a new txt file
with open("output/ips.txt","w") as f:
    for i in set(ips):
        f.write(i+"\n")

# Export extracted usernamse to a new txt file
with open("output/users.txt","w") as f:
    for u in set(users):
        f.write(u+"\n")

# Export extracted timestamps to a new txt file
with open("output/timestamps.txt","w") as f:
    for t in sorted(set(times)):
        f.write(t+"\n")


'''
5) Structured Log Parsing:
{
    "timestamp": "...",
    "level": "...",
    "message": "...",
    "ip": "..."
}
'''

all_logs = []

with open("input/logs.txt", "r") as f:
    lines = f.readlines()

for line in lines:
    info = re.match(r"(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2}) (INFO|ERROR|WARNING) (.*)",line)
    if info:
        log_data = {
            "date": info.group(1),
            "time": info.group(2),
            "level": info.group(3),
            "message": info.group(4).strip()
        }
        all_logs.append(log_data)

print("\nStructured Logs:\n")
for log in all_logs:
    print(log)

# Export structured logs to a new txt file
with open("output/structured_logs.txt", "w") as f:
    for log in all_logs:
        f.write(f"Date: {log['date']}\n")
        f.write(f"Time: {log['time']}\n")
        f.write(f"Level: {log['level']}\n")
        f.write(f"Message: {log['message']}\n")
        f.write("-" * 40 + "\n")

# Export structured logs to a new JSON file
with open("output/structured_logs.json", "w") as f:
    json.dump(all_logs, f, indent=4)

# Export structured logs to a new CSV file
with open("output/structured_logs.csv", "w", newline="") as f:
    fieldnames = ["date", "time", "level", "message"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(all_logs)
