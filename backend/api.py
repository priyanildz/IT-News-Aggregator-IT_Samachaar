import os
from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
# Removed: from bson.objectid import ObjectId - (This is correct, unnecessary import removed)

# ----------------------------------------------------------------------

# Setup
load_dotenv()

# Get the MongoDB connection string from environment variables
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    # If the .env file or MONGO_URI is missing, raise a clear error
    raise ValueError("MONGO_URI environment variable not set. Please create a .env file and ensure it contains your connection string.")

# Try to connect to MongoDB once when the server starts
try:
    client = MongoClient(MONGO_URI)
    # Ping the admin database to check the connection
    client.admin.command('ping') 
    print("Successfully connected to MongoDB! 🟢")
except Exception as e:
    print(f"Failed to connect to MongoDB: {e} 🔴")
    client = None # Set client to None if connection fails

# ----------------------------------------------------------------------

# Start Server
app = Flask(__name__)
# Enable CORS for all routes to allow connection from the React frontend
CORS(app) 

# ----------------------------------------------------------------------

# Define Endpoint
@app.route('/api/news', methods=['GET'])
def get_news():
    # Check if the MongoDB client is connected
    if client is None:
        return jsonify({"error": "Database connection failed at startup"}), 500
        
    # Query Database
    try:
        # Access the specified database and collection
        db = client['IT_Samachaar']
        collection = db['final_digest']
        
        # Fetch up to 10 documents
        articles = list(collection.find({}).limit(10)) 
    
    except Exception as e:
        # Handle potential query or connection issues
        print(f"Error querying database: {e}")
        return jsonify({"error": "Failed to retrieve articles from the database"}), 500

    # Clean Data
    # Convert MongoDB's ObjectId to a string for JSON serialization
    for article in articles:
        article['_id'] = str(article['_id'])

    # Send Response
    return jsonify(articles)

# ----------------------------------------------------------------------

# Run App
if __name__ == '__main__':
    # FIX for Windows socket error (OSError: [WinError 10038]):
    # Disables the automatic file reloader process that causes conflicts on restart.
    # debug=True is kept for error messages, but use_reloader is set to False.
    app.run(port=5000, debug=True, use_reloader=False)