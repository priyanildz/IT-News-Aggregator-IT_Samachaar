import requests
from bs4 import BeautifulSoup
from datetime import datetime
import uuid
import re

# --- Configuration ---
# Targeting the main technology section
INDIAN_EXPRESS_URL = 'https://indianexpress.com/section/technology/' 
SOURCE_NAME = 'Indian Express'

def scrape_indian_express():
    """
    RPA function to scrape articles from Indian Express.
    Uses a broad selector targeting links within the main content wrapper.
    """
    print(f"--- Starting scraping for {SOURCE_NAME} ---")
    
    try:
        # Use a custom User-Agent to mimic a real browser
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(INDIAN_EXPRESS_URL, headers=headers, timeout=15)
        response.raise_for_status() 
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to fetch {SOURCE_NAME}: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # AGGRESSIVE SELECTOR: Target all main article containers and grab the link inside.
    # We look for H2s or H3s within article blocks, which usually contain the link.
    article_elements = soup.select('div.articles a, h2 a, h3 a, .main-article-content a')
    
    scraped_data = []

    for title_link in article_elements:
        try:
            title = title_link.get_text(strip=True)
            url = title_link.get('href')

            # Basic filter to ensure we get meaningful links
            if not title or len(title.split()) < 3 or not url.startswith('http'):
                continue
            
            # --- STRUCTURED OUTPUT (Matches MongoDB Schema) ---
            article = {
                '_id': str(uuid.uuid4()),
                'source': SOURCE_NAME,
                'title': title,
                'url': url,
                'publication_date': datetime.utcnow().isoformat(),
                'status': 'RAW',
                
                # Full content for RAG: Use title as placeholder
                'full_text_content': f"Headline: {title}. Article URL: {url}",
                
                'category': 'Untagged', 
                'ai_summary': 'Placeholder: Analysis pending by Gemini RAG Pipeline.', 
            }
            
            scraped_data.append(article)

        except Exception as e:
            # print(f"Skipping {SOURCE_NAME} article due to parsing error: {e}") 
            continue

    print(f"--- Finished scraping {SOURCE_NAME}. Found {len(scraped_data)} articles. ---")
    return scraped_data

if __name__ == '__main__':
    # Test the function when run directly
    articles = scrape_indian_express()
    
    if articles:
        print("\nSuccessfully scraped data for Indian Express (first 3):")
        for article in articles[:3]:
            print(f" - Title: {article['title']}")
            print(f" - URL: {article['url']}")
    else:
        print("No articles were scraped.")