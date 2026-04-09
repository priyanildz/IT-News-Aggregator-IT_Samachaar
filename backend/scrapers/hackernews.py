import requests
from bs4 import BeautifulSoup
from datetime import datetime
import uuid
import re # For cleaning the URL

# Configuration for Hackernews
HACKERNEWS_URL = 'https://news.ycombinator.com/'
SOURCE_NAME = 'Hackernews'

def scrape_hackernews():
    """
    RPA function to scrape the front page of Hackernews for articles.
    Extracts the title, URL, and generates a placeholder for full content.
    """
    print(f"--- Starting scraping for {SOURCE_NAME} ---")
    
    try:
        # Use headers to mimic a real browser request
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(HACKERNEWS_URL, headers=headers, timeout=15)
        response.raise_for_status() # Check for bad status codes
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to fetch {SOURCE_NAME}: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Target elements that contain the articles (rows with class 'athing')
    story_rows = soup.select('.athing')
    
    scraped_data = []

    for row in story_rows:
        try:
            # 1. Title and URL
            title_link = row.select_one('.title a')
            if not title_link:
                continue

            title = title_link.get_text(strip=True)
            url = title_link.get('href')

            # Ensure the URL is absolute, fixing internal Hackernews links
            if url and url.startswith('item?'):
                url = HACKERNEWS_URL + url
                
            # Clean the URL to ensure it's a valid link format
            cleaned_url = re.sub(r'[^\x00-\x7F]+', '', url)
            
            # --- STRUCTURED OUTPUT (Matches MongoDB Schema) ---
            article = {
                '_id': str(uuid.uuid4()), # Unique ID for MongoDB
                'source': SOURCE_NAME,
                'title': title,
                'url': cleaned_url,
                'publication_date': datetime.utcnow().isoformat(),
                'status': 'RAW', # Initial status before RAG analysis
                
                # IMPORTANT: Placeholder for the full article text.
                # In a real project, we would visit the URL and scrape the whole body.
                # For this setup, we use the title + description for simplicity.
                'full_text_content': f"Headline: {title}. The article URL is {cleaned_url}. [Full content pending deep scrape]",
                
                # These fields are set later by the ML/RAG pipeline
                'category': 'Untagged', 
                'ai_summary': 'Placeholder: Analysis pending by Gemini RAG Pipeline.', 
            }
            
            scraped_data.append(article)

        except Exception as e:
            print(f"Skipping article due to parsing error: {e}")
            continue

    print(f"--- Finished scraping {SOURCE_NAME}. Found {len(scraped_data)} articles. ---")
    return scraped_data

if __name__ == '__main__':
    # Test the function when run directly
    articles = scrape_hackernews()
    
    if articles:
        print("\nSuccessfully scraped data for Hackernews:")
        for article in articles[:3]:
            print(f" - Title: {article['title']}")
            print(f" - URL: {article['url']}")
            print(f" - ID: {article['_id']}")
    else:
        print("No articles were scraped.")