"""
scraper.py
----------
Scrapes product listings from a target site and saves them as products.json.

You MUST edit the CONFIG section below to match the site you're scraping
(each site's HTML is different, so the CSS selectors have to change).

Run:
    python scraper.py
"""

import json
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# ======================= CONFIG (edit this) =======================
BASE_URL = "https://www.amazon.eg/s?i=electronics&rh=n%3A21832907031&s=popularity-rank&fs=true&language=en"

# CSS selectors — inspect the target page (right click -> Inspect) and
# fill these in. This is the only part that changes per website.
SELECTORS = {
    "product_card": "[data-asin]",
    "name": "div.acsProductBlockV2__product-title span.a-truncate-full, h2",
    "price": "span.a-price .a-offscreen",
    "description": "",                       # not present in these cards
    "url": "a[href*='/dp/']",
    "category": "span.acsProductBlockV2__contributor-value",
    "rating": "i[aria-label*='out of 5 stars']",
    "review_count": "span.acsProductBlockV2__rating__review-count",
}
# ====================================================================

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def safe_text(node):
    return node.get_text(strip=True) if node else ""


def scrape_page(url: str) -> list[dict]:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            executable_path="C:/Program Files/Google/Chrome/Application/chrome.exe",
            headless=False,
        )
        page = browser.new_page(
            user_agent=HEADERS["User-Agent"],
            locale="en-US",
        )
        page.goto(url, wait_until="domcontentloaded", timeout=60_000)
        page.wait_for_timeout(3_000)
        soup = BeautifulSoup(page.content(), "html.parser")
        browser.close()

    products = []
    for card in soup.select(SELECTORS["product_card"]):
        if not card.get("data-asin"):
            continue
        name = safe_text(card.select_one(SELECTORS["name"]))
        if not name:
            continue  # skip anything that isn't really a product card

        link_tag = card.select_one(SELECTORS["url"])
        link = (
            urljoin(url, link_tag["href"])
            if link_tag and link_tag.has_attr("href")
            else ""
        )

        rating_tag = card.select_one(SELECTORS["rating"])
        rating = rating_tag.get("aria-label", "") if rating_tag else ""

        products.append({
            "id": f"prod-{abs(hash(name + link))}",
            "name": name,
            "price": safe_text(card.select_one(SELECTORS["price"])),
            "description": safe_text(card.select_one(SELECTORS["description"])) if SELECTORS["description"] else "",
            "category": safe_text(card.select_one(SELECTORS["category"])),
            "rating": rating,
            "review_count": safe_text(card.select_one(SELECTORS["review_count"])),
            "url": link,
        })
    return products


def main():
    print(f"Scraping {BASE_URL} ...")
    try:
        all_products = scrape_page(BASE_URL)
    except Exception as e:
        print(f"  failed: {e}")
        return
    if not all_products:
        print("  no products found; keeping the existing products.json.")
        return

    with open("products.json", "w", encoding="utf-8") as f:
        json.dump(all_products, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(all_products)} products to products.json")


if __name__ == "__main__":
    main()
