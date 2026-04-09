import time
import os
import sys
from datetime import datetime

# Add the 'scrapers' directory to the Python path so we can import the modules
# This is necessary because 'scrapers' is a sub-directory
sys.path.append(os.path.join(os.path.dirname(__file__), 'scrapers'))

# Import all four stable scraping functions
from scrapers.hackernews import scrape_hackernews 
from scrapers.devto import scrape_devto 
from scrapers.medium import scrape_medium 
from scrapers.indian_express import scrape_indian_express 
from ingestion import insert_raw_articles, connect_to_mongodb # Import ingestion logic
from generation_agent import run_rag_analysis # Import the RAG Agent function

# --- Master Configuration ---
ALL_SCRAPERS = [
    scrape_hackernews,
    scrape_devto, 
    scrape_medium, 
    scrape_indian_express, 
]

DB_NAME = "IT_Samachaar"
COLLECTION_NAME_RAW = "raw_articles"


def run_data_collection_pipeline():
    """
    Orchestrates the entire daily RPA, Ingestion, and Intelligence process.
    """
    start_time = time.time()
    all_articles = []

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] --- Starting IT Samachaar Data Collection Pipeline ---")

    # 1. Connect and clear old raw data
    try:
        client = connect_to_mongodb()
        if client:
            db = client[DB_NAME]
            # Clear the old raw articles to ensure a fresh feed for the day
            db[COLLECTION_NAME_RAW].delete_many({}) 
            print(f"SUCCESS: Cleared all previous documents from '{COLLECTION_NAME_RAW}'.")
            client.close()
    except Exception as e:
        print(f"CRITICAL ERROR: Failed to clear MongoDB collection. Skipping run. Error: {e}")
        return

    # 2. Execute all scraping agents
    for scraper_func in ALL_SCRAPERS:
        try:
            articles = scraper_func()
            all_articles.extend(articles)
        except Exception as e:
            print(f"ERROR: {scraper_func.__name__} failed with error: {e}")

    total_scraped = len(all_articles)
    if total_scraped == 0:
        print("WARNING: No articles were successfully scraped from any source.")
        return

    # 3. Ingest raw data into MongoDB
    total_inserted = insert_raw_articles(all_articles)

    # 4. Trigger Intelligence Layer (ML Classification & Semantic Generation)
    try:
        print("\nACTION: Launching Intelligence Layer (Gemini RAG + ML Classification)...")
        # FIX: Call run_rag_analysis with NO arguments
        run_rag_analysis() 
        print("SUCCESS: Intelligence pipeline completed.")
    except Exception as e:
        print(f"ERROR: Failed to run intelligence pipeline. Error: {e}")

    # 5. Final Report
    end_time = time.time()
    duration = round(end_time - start_time, 2)

    print("\n--- Pipeline Summary ---")
    print(f"Total time elapsed: {duration} seconds")
    print(f"Total articles scraped: {total_scraped}")
    print(f"Total articles ingested into MongoDB: {total_inserted}")
    print("------------------------")


if __name__ == '__main__':
    run_data_collection_pipeline()