# BJJ Database & Analytics Portfolio Project

# Overview

This repository contains a comprehensive data pipeline and analytics project focused on Brazilian Jiu-Jitsu (BJJ) competition data. The goal is to collect, clean, store, and visualize BJJ match data from various sources, such as BJJHeroes and SmoothComp. Additionally, this project includes dashboard development and a web front-end to showcase insights interactively.

# Project Structure
BJJ_Database/
│── data/                        # Raw and processed datasets (CSV, JSON, Parquet)
│    ├── raw/                    # Scraped raw data
│    ├── processed/               # Cleaned and transformed data
│    ├── logs/                    # Log files for debugging scrapers
│── scrapers/                     # Web scrapers for BJJ data collection
│    ├── bjj_heroes_scraper/      # BJJHeroes scrapers
│    ├── smoothcomp_scraper/      # SmoothComp scrapers
│    ├── utils/                   # Common utilities (pagination, logging, etc.)
│── dashboards/                   # Power BI, Dash, or Streamlit visualizations
│    ├── power_bi/                # PBIX files & DAX scripts
│    ├── streamlit_app/           # Streamlit Python scripts
│    ├── dash_app/                # Plotly Dash app
│── backend/                      # API and data handling (Flask, FastAPI, Django)
│    ├── api/                     # API endpoints for data retrieval
│    ├── models/                  # Database models (SQLAlchemy, etc.)
│    ├── services/                # Business logic (data cleaning, transformations)
│── frontend/                     # Web front-end (React, Vue, Svelte, etc.)
│    ├── public/                  # Static assets (CSS, images)
│    ├── src/                     # Source code
│    ├── components/               # Reusable UI components
│    ├── pages/                    # Page-specific code
│── notebooks/                     # Jupyter Notebooks for data exploration
│── config/                        # Configuration files (.env, YAML, JSON)
│── tests/                         # Unit and integration tests
│── scripts/                       # Standalone scripts (data transformations, automation)
│── docs/                          # Documentation for the project
│── requirements.txt                # Python dependencies
│── README.md                      # Project documentation
│── .gitignore                      # Ignored files
│── pyproject.toml                  # Optional - modern package management
│── docker-compose.yml              # If using Docker for services
│── .env                            # Environment variables (DO NOT COMMIT)

# Features & Components

1. Web Scraping

- Scrapes BJJ match data from sources like BJJHeroes & SmoothComp.

- Uses Python, BeautifulSoup, and Selenium for data extraction.

- Automated logging and error handling for robustness.

2. Data Storage & Processing

- Stores structured data in CSV, JSON, or a database (future expansion).

- Cleans and processes data using Pandas & SQL.

- Unique match IDs are generated to avoid duplication.

3. Dashboard & Visualizations

- Power BI reports to display key BJJ statistics.

- Streamlit or Dash app for interactive web-based analytics.

- Potential for real-time updates via API integration.

4. API Development

- Flask or FastAPI for retrieving match and fighter data.

- Allows seamless connection between the backend and frontend.

5. Front-End Web Application

- Interactive React/Vue app for data exploration.

- Displays fighter stats, match history, and insights.

- Designed for easy navigation and filtering.

Technologies Used

- Python (Scraping, Data Processing, APIs, Dashboards)

- Pandas, SQLAlchemy (Data Transformation & Storage)

- BeautifulSoup, Selenium (Web Scraping)

- Flask/FastAPI (Backend API Development)

- Power BI, Streamlit, Plotly Dash (Visualization & Reporting)

- React/Vue/Svelte (Front-End Development)

- Docker (Containerization & Scalability)


Setup & Installation

1. Clone the Repository

git clone https://github.com/yourusername/BJJ_Database.git
cd BJJ_Database

2. Install Dependencies

pip install -r requirements.txt

If using pyproject.toml, install dependencies via:

pip install poetry
poetry install

3. Set Up Environment Variables

Copy .env.example to .env and configure API keys, database credentials, etc.

4. Run the Web Scrapers

python scrapers/bjj_heroes_scraper/scrape.py
python scrapers/smoothcomp_scraper/scrape.py

5. Launch Dashboard

For Streamlit:

streamlit run dashboards/streamlit_app/app.py

For Plotly Dash:

python dashboards/dash_app/app.py

6. Start Backend API

uvicorn backend.api.main:app --reload

7. Run Frontend App

If using React:

Future Enhancements

Database Integration (PostgreSQL for structured storage)

Automated Data Refresh (Scheduled scraping & data pipeline)

Machine Learning Models (Predictive analytics for match outcomes)

User Authentication (Login system for personalized experience)


Contact & Portfolio

This project is part of my portfolio to showcase my skills in data engineering, analytics, and web development. If you're interested in my work, feel free to reach out!

LinkedIn: 

GitHub: Your GitHub


