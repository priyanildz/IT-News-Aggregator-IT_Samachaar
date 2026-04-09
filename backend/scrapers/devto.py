import requests
from bs4 import BeautifulSoup
from datetime import datetime
import uuid
import re

# --- Configuration ---
DEVTO_URL = 'https://dev.to/t/webdev' # Targeting a specific, structured tag page
SOURCE_NAME = 'Dev.to'

def scrape_devto():
    """
    RPA function to scrape articles from a Dev.to tag page.
    Uses robust selection targeting the core article link container.
    """
    print(f"--- Starting scraping for {SOURCE_NAME} ---")
    
    try:
        # Use a custom User-Agent to mimic a real browser
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(DEVTO_URL, headers=headers, timeout=15)
        response.raise_for_status() 
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to fetch {SOURCE_NAME}: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # NEW ROBUST SELECTOR: Targeting all top-level article links within the main feed area.
    # We look for H2 tags which universally contain the title links on Dev.to.
    article_links = soup.select('div[id*="substories"] h2 a, article h2 a, main div a.crayons-story__summary__title')
    
    scraped_data = []

    for title_link in article_links:
        try:
            title = title_link.get_text(strip=True)
            url_path = title_link.get('href')

            if not title or not url_path:
                continue

            # Ensure URL is absolute
            url = url_path if url_path.startswith('http') else f"https://dev.to{url_path}"

            # Summary snippet is usually hard to get; we use the title for initial RAG grounding
            description = title
            
            # --- STRUCTURED OUTPUT (Matches MongoDB Schema) ---
            article = {
                '_id': str(uuid.uuid4()),
                'source': SOURCE_NAME,
                'title': title,
                'url': url,
                'publication_date': datetime.utcnow().isoformat(),
                'status': 'RAW',
                
                # Full content for RAG
                'full_text_content': f"Headline: {title}. Summary/Snippet: {description}. Article URL: {url}",
                
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
    articles = scrape_devto()
    
    if articles:
        print("\nSuccessfully scraped data for Dev.to (first 3):")
        for article in articles[:3]:
            print(f" - Title: {article['title']}")
            print(f" - URL: {article['url']}")
    else:
        print("No articles were scraped.")