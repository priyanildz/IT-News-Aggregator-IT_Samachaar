import requests
from bs4 import BeautifulSoup
from datetime import datetime
import uuid
import re

# --- Configuration ---
# Targeting a reliable Medium tag RSS feed, which is more stable than scraping the main page.
MEDIUM_RSS_URL = 'https://medium.com/feed/tag/software-engineering' 
SOURCE_NAME = 'Medium'

def scrape_medium():
    """
    RPA function to scrape articles from Medium using its RSS feed endpoint.
    RSS feeds provide structured XML, making them highly reliable.
    """
    print(f"--- Starting scraping for {SOURCE_NAME} (via RSS) ---")
    
    try:
        # Use a custom User-Agent for reliability
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(MEDIUM_RSS_URL, headers=headers, timeout=15)
        response.raise_for_status() 
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to fetch {SOURCE_NAME}: {e}")
        return []

    # Parse the XML/RSS content
    soup = BeautifulSoup(response.text, 'xml')
    
    # Target elements are <item> tags in the RSS feed
    articles_items = soup.find_all('item')
    
    scraped_data = []

    for item in articles_items:
        try:
            title_tag = item.find('title')
            url_tag = item.find('link')
            description_tag = item.find('description')
            pub_date_tag = item.find('pubDate')

            # Ensure necessary data is present
            if not all([title_tag, url_tag, description_tag]):
                continue

            title = title_tag.get_text(strip=True)
            url = url_tag.get_text(strip=True)
            
            # The description often contains the full HTML body or a summary
            description_raw = description_tag.get_text(strip=True)
            
            # --- Clean description to get a simple text snippet (for RAG context) ---
            # Use BeautifulSoup again to strip HTML from the description snippet
            desc_soup = BeautifulSoup(description_raw, 'html.parser')
            description = desc_soup.get_text(strip=True)[:500] + "..." # Limit length for RAG context
            
            # --- Publication Date ---
            pub_date = pub_date_tag.get_text(strip=True) if pub_date_tag else datetime.utcnow().isoformat()

            # --- STRUCTURED OUTPUT (Matches MongoDB Schema) ---
            article = {
                '_id': str(uuid.uuid4()),
                'source': SOURCE_NAME,
                'title': title,
                'url': url,
                'publication_date': datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %Z').isoformat() if pub_date_tag else pub_date,
                'status': 'RAW',
                
                # Full content for RAG: Use cleaned description and title
                'full_text_content': f"Headline: {title}. Snippet: {description}",
                
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
    articles = scrape_medium()
    
    if articles:
        print("\nSuccessfully scraped data for Medium (first 3):")
        for article in articles[:3]:
            print(f" - Title: {article['title']}")
            print(f" - URL: {article['url']}")
            print(f" - Date: {article['publication_date']}")
    else:
        print("No articles were scraped.")