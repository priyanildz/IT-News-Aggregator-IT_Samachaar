# import requests
# from bs4 import BeautifulSoup
# from datetime import datetime
# import uuid

# # --- Configuration ---
# GADGETS360_URL = 'https://www.gadgets360.com/news'
# SOURCE_NAME = 'Gadgets 360'

# def scrape_gadgets360():
#     """
#     Robust scraper for Gadgets360 that avoids 403 Forbidden using realistic headers & session.
#     """
#     print(f"--- Starting scraping for {SOURCE_NAME} ---")

#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#                       "AppleWebKit/537.36 (KHTML, like Gecko) "
#                       "Chrome/122.0.0.0 Safari/537.36",
#         "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
#         "Accept-Language": "en-US,en;q=0.9",
#         "Referer": "https://www.google.com/",
#         "DNT": "1",
#         "Connection": "keep-alive",
#         "Upgrade-Insecure-Requests": "1",
#         "Cache-Control": "no-cache"
#     }

#     try:
#         session = requests.Session()
#         session.headers.update(headers)

#         # STEP 1: Visit home page first to get cookies (helps pass anti-bot)
#         session.get("https://www.gadgets360.com/", timeout=15)

#         # STEP 2: Now visit the actual news page
#         response = session.get(GADGETS360_URL, timeout=15)
#         response.raise_for_status()

#     except requests.exceptions.RequestException as e:
#         print(f"ERROR: Failed to fetch {SOURCE_NAME}: {e}")
#         return []

#     soup = BeautifulSoup(response.text, "html.parser")

#     # Updated selector for Gadgets360 news page
#     articles = soup.select("div.story_list.row div.story_list_content")

#     scraped_data = []

#     for article in articles:
#         try:
#             title_tag = article.select_one("h2 a") or article.select_one("h3 a")
#             desc_tag = article.select_one("p")
#             if not title_tag:
#                 continue

#             title = title_tag.get_text(strip=True)
#             url = title_tag["href"]
#             if not url.startswith("http"):
#                 url = f"https://www.gadgets360.com{url}"

#             description = desc_tag.get_text(strip=True) if desc_tag else title

#             scraped_data.append({
#                 "_id": str(uuid.uuid4()),
#                 "source": SOURCE_NAME,
#                 "title": title,
#                 "url": url,
#                 "publication_date": datetime.utcnow().isoformat(),
#                 "status": "RAW",
#                 "full_text_content": f"Headline: {title}. Summary/Snippet: {description}. Article URL: {url}",
#                 "category": "Untagged",
#                 "ai_summary": "Placeholder: Analysis pending by Gemini RAG Pipeline."
#             })

#         except Exception as e:
#             print(f"Skipping article due to error: {e}")
#             continue

#     print(f"--- Finished scraping {SOURCE_NAME}. Found {len(scraped_data)} articles. ---")
#     return scraped_data


# if __name__ == "__main__":
#     articles = scrape_gadgets360()
#     if articles:
#         print("\n✅ Successfully scraped Gadgets 360:")
#         for a in articles[:3]:
#             print(f" - {a['title']}")
#             print(f"   {a['url']}")
#     else:
#         print("❌ No articles scraped.")
