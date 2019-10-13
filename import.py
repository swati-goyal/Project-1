import requests
import pprint

res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "K0pOqH7V3rc9YKReYXz40g", "isbns": "0765317508"})
pprint.pprint(res.json())