import requests
import json
import csv
import time
import datetime

with open("config.txt", "r") as file:
    USER = file.readline()[:-1]
    PASS = file.readline()

url = 'https://api.intrinio.com/historical_data?identifier=AAPL&&sort_order=asc&item=dividend'
#url = 'https://api.intrinio.com/prices?identifier=AAPL&sort_order=asc&page_number=1'
s = requests.Session()
s.auth = (USER, PASS)



dividends = json.loads(s.get(url).text)
print(dividends)
for entry in dividends["data"]:
    year, month, day = entry["date"].split("-")
    entry["date"] = datetime.date(int(year), int(month), int(day))

print(dividends["data"][1]["date"] - dividends["data"][0]["date"])
start = dividends["data"][0]["date"]
window = datetime.date(start.year + 5, start.month, start.day)

dates_ahead = []

for entry in dividends["data"]:
    dates_ahead.append(str(window - entry["date"]).split(" ")[0])
    print(str(window - entry["date"]))

dates_ahead = list(map(lambda x: abs(int(x)), dates_ahead))
curr_pos = dates_ahead.index(min(dates_ahead))
print(curr_pos)

bottom_bound = 0

#This means that when we reach the end with our bound of sliding window we will never get another run
while curr_pos < len(dividends["data"]):
    increase = dividends["data"][curr_pos]["value"] / dividends["data"][bottom_bound]["value"]
    print(increase)
    if increase > 50:
        tri_start = bottom_bound

    bottom_bound += 1
    curr_pos += 1



print("Pages of dividend", dividends["total_pages"])

'''
total_pages = int(r["total_pages"])
print(total_pages)
pages_stored = []
for page in range(1, 3 + 1):
    url = 'https://api.intrinio.com/prices?identifier=AAPL&sort_order=asc&page_number={}'.format(page)
    s = requests.Session()
    s.auth = (USER, PASS)

    pages_stored.append(json.loads(s.get(url).text))
    print("Done Page")

print(pages_stored)

#Simple Total return index calculation
with open('output.csv', 'w') as csvfile:
    fieldnames = ['stock_price', 'date', 'split_ratio', 'dividend_value']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for r in pages_stored:
        for i in r["data"]:
            dividend = None
            for k in dividends['data']:
                if i['date'] == k['date']:
                    dividend = k["value"]
            writer.writerow({'date': i["date"], 'stock_price': i["adj_close"],
                             'split_ratio': i["split_ratio"], 'dividend_value': dividend})
'''