# Agentic Campaign Optimization Engine

This workshop demo showcases an AI-driven marketing optimization experience in Streamlit. The app simulates a campaign agent that monitors performance, detects underperformers, rewrites ad creative, and recommends budget shifts.

## Project Structure
- `app.py`: Main Streamlit application shell with page navigation.
- `data/data_generation.py`: Dummy marketing data generator with intentional underperforming segments.
- `requirements.txt`: Python dependencies.

## Getting Started
1. Create a Python environment.
2. Install dependencies: `pip install -r requirements.txt`
3. Run the app: `streamlit run app.py`

## Features
- Campaign Dashboard with Spend vs Conversions and CPA by Platform.
- Anomaly Detection to surface poor-performing segments.
- Agentic Creative Optimization simulation for ad copy rewrites.
- Budget Reallocation Engine with current and recommended allocations.
