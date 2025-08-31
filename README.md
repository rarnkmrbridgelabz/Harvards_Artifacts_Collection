🎨 Harvard Art Museums ETL & Data Exploration Platform

An interactive, end-to-end ETL (Extract, Transform, Load) and data exploration platform built with Streamlit, powered by the Harvard Art Museums public API.

This platform enables users to:
✅ Explore Harvard’s digital art collections dynamically
✅ Extract data directly from the Harvard Art Museums API
✅ Transform & filter essential metadata for research or projects
✅ Load and persist data into a structured relational database (MySQL / SQLite)
✅ Interactively query and visualize artworks, media, and colors
✅ Gain insights into culture, classification, medium, and time periods

🚀 Features

Dynamic API Integration: Pull artworks by classification (Paintings, Sculptures, Prints, etc.)
ETL Pipeline: Extract → Clean/Transform → Load into database
Database Support: Choose between SQLite (lightweight, local) or MySQL (scalable, production-ready)
Interactive Exploration:
Browse metadata (titles, cultures, periods, mediums, etc.)
Explore media details (images, counts, ranks, timelines)
Analyze color palettes from artworks
Search & Filter: Query by classification, culture, or time period
Visualization: Interactive charts for color distributions, cultural breakdowns, and periods

🛠️ Tech Stack

Frontend / UI: Streamlit
Backend / API: Harvard Art Museums API
Database: SQLite / MySQL
Python Libraries:
requests → API integration
pandas → data transformation & analysis
mysql-connector-python or sqlite3 → database persistence
matplotlib / seaborn → data visualization
streamlit → web application
