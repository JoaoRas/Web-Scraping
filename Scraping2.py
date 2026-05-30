import requests
from bs4 import BeautifulSoup
import json

url = "https://infosimples.com/vagas/desafio/stellarcraft/product.html"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)

if response.status_code != 200:
    raise Exception("Erro ao acessar página")

soup = BeautifulSoup(response.content, "html.parser")


def safe_text(el):
    return el.get_text(strip=True) if el else None


def clean_price(price_str):
    if not price_str:
        return None
    try:
     return float(price_str.replace("R$", "").replace(".", "").replace(",", ".").strip())
    except:
        return None


data = {
    "title": safe_text(soup.select_one("#product_title")),
    "brand": safe_text(soup.select_one(".product-brand")),
    "categories": [safe_text(i) for i in soup.select("nav[aria-label='breadcrumbs'] a")],
    "description": safe_text(soup.select_one("#tab-description")),
    "skus": [],
    "specification": [],
    "reviews": [],
    "reviews_average_score": None,
    "url": url
}

for sku in soup.select(".variant-btn"):
    name = safe_text(sku.select_one(".vname"))
    available = "unavailable" not in sku.get("class", [])

    data["skus"].append({
        "name": name,
        "current_price": clean_price(sku.get("data-price")) if available else None,
        "old_price": clean_price(sku.get("data-old-price")) if available else None,
        "available": available
    })

for row in soup.select("#tab-specs tr"):
    cols = row.select("td")
    if len(cols) >= 2:
        data["specification"].append({
            "label": safe_text(cols[0]),
            "value": safe_text(cols[1])
        })

for review in soup.select("#tab-reviews .review-card"):
    header = review.select_one(".review-header")
reviews = []

for review in soup.select("#tab-reviews .review-card"):
    name = review.select_one(".reviewer-name").get_text(strip=True)

    date = review.select_one(".reviewer-date").get_text(strip=True)
    text = review.select_one(".review-text").get_text(strip=True)
    stars_text = review.select_one(".review-stars").get_text(strip=True)
    score = stars_text.count("★")

    reviews.append({
        "name": name,
        "date": date,
        "score": score,
        "text": text
    })

data["reviews"] = reviews

avg = soup.select_one(".avg-score")
if avg:
    data["reviews_average_score"] = float(safe_text(avg).replace(",", "."))

with open("produto.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Arquivo salvo com sucesso!")