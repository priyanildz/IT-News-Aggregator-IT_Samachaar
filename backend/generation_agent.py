import os
import time
import uuid
import json
import random
from datetime import datetime

from google import genai
from google.genai import types # Keep types for GenerateContentConfig
from dotenv import load_dotenv

from ingestion import connect_to_mongodb, upsert_final_digest

# Load environment variables
load_dotenv()

# --- Configuration ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DB_NAME = "IT_Samachaar"
COLLECTION_NAME_RAW = "raw_articles"
COLLECTION_NAME_FINAL = "final_digest"

# --- ML MOCK: Custom Topic Classification Model ---
# In a real project, this would be a loaded scikit-learn or FastText model.
# For simplicity, we use a heuristic based on keywords to simulate classification.

# Defined topics for the frontend filters
TOPIC_KEYWORDS = {
    'AI/ML': ['gemini', 'llm', 'machine learning', 'artificial intelligence', 'neural network', 'data science', 'transformer model'],
    'Cloud/DevOps': ['kubernetes', 'aws', 'azure', 'gcp', 'docker', 'devops', 'terraform', 'serverless', 'microservices'],
    'Software Engineering': ['python', 'rust', 'go', 'javascript', 'framework', 'testing', 'refactoring', 'architecture', 'c++'],
    'Security': ['security', 'vulnerability', 'exploit', 'bug bounty', 'encryption', 'ssl', 'cybersecurity'],
    'WebDev': ['react', 'vue', 'frontend', 'backend', 'web assembly', 'html', 'css', 'api', 'vercel', 'next.js'],
}
DEFAULT_CATEGORY = 'Software Engineering'

def classify_article(article_text):
    """
    Simulates a custom ML classifier by assigning a topic based on keyword frequency.
    """
    text_lower = article_text.lower()
    scores = {}
    
    # Calculate score for each category
    for category, keywords in TOPIC_KEYWORDS.items():
        score = sum(text_lower.count(k) for k in keywords)
        scores[category] = score
    
    # Find the category with the highest score
    if not scores or all(score == 0 for score in scores.values()):
        return DEFAULT_CATEGORY
    
    # Simple selection of the top category
    best_category = max(scores, key=scores.get)
    return best_category

# --- RAG Core: Semantic Generation Agent ---

def run_rag_analysis():
    """
    Master function to retrieve raw data, run classification, and execute the RAG pipeline
    to generate curated, final summaries.
    """
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] --- Starting RAG Analysis and Curation ---")
    
    if not GEMINI_API_KEY:
        print("CRITICAL ERROR: GEMINI_API_KEY not set. Skipping RAG Analysis.")
        return 0

    client = connect_to_mongodb()
    if not client:
        return 0

    db = client[DB_NAME]
    raw_collection = db[COLLECTION_NAME_RAW]
    final_articles = []
    
    # 1. RETRIEVE all raw articles
    raw_articles = list(raw_collection.find({}))
    total_raw = len(raw_articles)
    print(f"Retrieved {total_raw} articles for processing.")

    # Only process a small batch to stay within API rate limits during testing
    articles_to_process = random.sample(raw_articles, min(len(raw_articles), 10))

    try:
        gemini_client = genai.Client(api_key=GEMINI_API_KEY)
        
        # System instruction to guide the LLM's persona and output format
        # 🛠️ FIX: Updated prompt for a more comprehensive 5-sentence summary
        system_prompt = (
            "You are an expert IT Samachaar editorial agent. Your task is to analyze the provided article context "
            "and generate a **comprehensive, 3-sentence summary** that covers the **core technical problem**, "
            "make sure to avoid classsification topic in summary. the **solution presented**, and the **final implications** for a senior software engineer, "
            "cloud architect, or data scientist. Do not include placeholders. Be formal and professional."
        )

        for article in articles_to_process:
            try:
                # --- Step 2a: Mock Classification ---
                category = classify_article(article['full_text_content'] + article['title'])
                
                # --- Step 2b: Semantic Generation (RAG) ---
                
                # The raw text serves as the grounding context (RAG context)
                grounding_context = article['full_text_content']
                
                # The user query instructs the model on what to produce
                user_query = (
                    f"Based ONLY on the following content, classify the article's main topic as one of the following: "
                    f"'{category}', 'AI/ML', 'Cloud/DevOps', 'Software Engineering', 'Security', or 'WebDev'. "
                    f"Then, generate a 3-sentence summary based on the system instructions. make sure to avoid classsification topic in summary."
                    f"Content Title: {article['title']}\n\nContent: {grounding_context}"
                )

                # Call Gemini for the cognitive task
                response = gemini_client.models.generate_content(
                    model='gemini-2.5-flash-preview-09-2025',
                    contents=user_query,
                    config=types.GenerateContentConfig(
                        # FIX: Passing system_prompt directly as a string to system_instruction
                        system_instruction=system_prompt,
                        # Optional: Enforce structured output via Pydantic/JSON Schema if needed for precise parsing
                    )
                )

                # --- Step 2c: Parse Output (Simplifying response parsing) ---
                # Since we asked for two distinct pieces of info, we just grab the full text output for now
                ai_summary = response.text.strip()
                
                # --- Step 3: Prepare Final Document ---
                final_doc = {
                    '_id': article['_id'],
                    'source': article['source'],
                    'title': article['title'],
                    'url': article['url'],
                    'publication_date': article['publication_date'],
                    'category': category, # Use the mock classified category for the frontend
                    'ai_summary': ai_summary,
                }
                
                final_articles.append(final_doc)
                # print(f" - Analyzed and summarized: {article['title']}")

            except Exception as e:
                print(f"WARNING: Failed RAG analysis for article {article['title']}. Error: {e}")
                continue

    except Exception as e:
        print(f"CRITICAL ERROR: Failed to initialize or communicate with Gemini API. Error: {e}")
        return 0
    finally:
        client.close()

    # 4. UPSERT final results into MongoDB
    total_inserted = upsert_final_digest(final_articles)
    
    print(f"--- RAG Analysis Complete. Generated {total_inserted} polished articles. ---")
    return total_inserted

if __name__ == '__main__':
    # This block is for testing the agent independently
    run_rag_analysis()