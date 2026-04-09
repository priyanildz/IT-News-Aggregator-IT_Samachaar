import time
import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "IT_Samachaar"
COLLECTION_NAME_RAW = "raw_articles"
COLLECTION_NAME_FINAL = "final_digest" # For the polished RAG output

def connect_to_mongodb():
    """Establishes and returns a MongoDB client connection."""
    if not MONGO_URI:
        # In a real environment, this should raise a fatal error
        print("CRITICAL ERROR: MONGO_URI environment variable not found. Check your .env file.")
        return None
    
    # Connect using MongoClient
    client = MongoClient(MONGO_URI)
    
    # The ismaster command is a lightweight way to check the connection
    try:
        client.admin.command('ismaster')
        # print("SUCCESS: Connected to MongoDB Atlas.") # Commented out to reduce console clutter in the pipeline
        return client
    except Exception as e:
        print(f"CRITICAL ERROR: Cannot connect to MongoDB Atlas. Check URI and network access. Error: {e}")
        return None

def insert_raw_articles(articles):
    """
    Inserts a list of raw article documents into the dedicated collection (for RAG consumption).
    """
    client = connect_to_mongodb()
    if not client:
        return 0

    db = client[DB_NAME]
    collection = db[COLLECTION_NAME_RAW]
    
    if not articles:
        print("Warning: No articles provided for insertion.")
        client.close()
        return 0
    
    try:
        # Insert articles into MongoDB
        result = collection.insert_many(articles)
        # print(f"SUCCESS: Inserted {len(result.inserted_ids)} raw articles into '{COLLECTION_NAME_RAW}'.")
        return len(result.inserted_ids)
    except Exception as e:
        print(f"ERROR: Failed to insert articles into MongoDB: {e}")
        return 0
    finally:
        client.close()

def upsert_final_digest(final_articles):
    """
    Inserts or updates the final, categorized, and summarized articles 
    into the 'final_digest' collection, which the frontend consumes.
    """
    client = connect_to_mongodb()
    if not client:
        return 0

    db = client[DB_NAME]
    final_collection = db[COLLECTION_NAME_FINAL]
    
    if not final_articles:
        print("Warning: No final articles provided for upsertion.")
        client.close()
        return 0
    
    # Use delete_many(old) and insert_many(new) for simplicity
    # This ensures the dashboard always gets a fresh daily feed without complex upsert logic
    
    try:
        # 1. Clear the old final digest (since we run daily)
        final_collection.delete_many({})
        
        # 2. Insert the new final articles
        result = final_collection.insert_many(final_articles)
        print(f"SUCCESS: Inserted {len(result.inserted_ids)} final articles into '{COLLECTION_NAME_FINAL}'.")
        return len(result.inserted_ids)
    except Exception as e:
        print(f"ERROR: Failed to upsert final articles into MongoDB: {e}")
        return 0
    finally:
        client.close()


if __name__ == '__main__':
    print("MongoDB Ingestion script loaded. It provides functions for connecting and inserting data.")