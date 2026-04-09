# IT News Aggregator (IT_Samachaar)

IT News Aggregator (IT_Samachaar) is a web scraping and news aggregation project that collects IT/tech articles from multiple platforms, stores them in MongoDB, and serves them to a React dashboard.

## Features

- Scrapes articles from multiple sources (Dev.to, Hacker News, Medium, Gadgets360, Indian Express)
- Processes and stores news in MongoDB
- Exposes a Flask API endpoint for frontend consumption
- Displays aggregated content in a React + Vite dashboard

## Project Structure

```
it_samachaar/
	backend/
		api.py
		generation_agent.py
		ingestion.py
		pipeline.py
		scrapers/
	dashboard/
		src/
		package.json
	it-samachaar-frontend/
		src/
		package.json
```

Notes:
- `dashboard/` is the primary frontend.
- `it-samachaar-frontend/` appears to be an alternate/older frontend copy.

## Tech Stack

- Backend: Flask, Flask-CORS, PyMongo, python-dotenv
- Database: MongoDB
- Frontend: React + Vite

## Prerequisites

- Python 3.10+
- Node.js 18+
- npm
- MongoDB Atlas or local MongoDB instance

## Backend Setup

From project root:

```bash
cd backend
pip install flask flask-cors pymongo python-dotenv
```

Create a `.env` file inside `backend/`:

```env
MONGO_URI=your_mongodb_connection_string
```

Run backend server:

```bash
python api.py
```

Backend runs at: `http://localhost:5000`

Available endpoint:
- `GET /api/news`

## Frontend Setup (Dashboard)

From project root:

```bash
cd dashboard
npm install
npm run dev
```

Frontend runs at: `http://localhost:5173`

## Optional Alternate Frontend

If you want to run the alternate frontend:

```bash
cd it-samachaar-frontend
npm install
npm run dev
```

## Run Full Project

Use two terminals:

1. Terminal 1 (Backend)

```bash
cd backend
python api.py
```

2. Terminal 2 (Frontend)

```bash
cd dashboard
npm run dev
```

Then open `http://localhost:5173`.

## Screenshots

### Dashboard View 1

![Dashboard View 1](assets/Screenshot%202026-04-09%20152152.png)

### Dashboard View 2

![Dashboard View 2](assets/Screenshot%202026-04-09%20152205.png)
