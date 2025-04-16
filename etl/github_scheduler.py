#!/usr/bin/env python3
"""
BART ETL Scheduler for GitHub Actions
This script runs the ETL job once and exits, suitable for GitHub Actions.
"""

import logging
import os
import sqlite3
from datetime import datetime
from etl.extractor import BartDataExtractor
from etl.transformer import BartDataTransformer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def init_sqlite_db():
    """Initialize SQLite database if it doesn't exist"""
    db_path = os.environ.get('DATABASE_PATH', 'data/bart_history.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Create tables if they don't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS departures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station TEXT,
            destination TEXT,
            platform TEXT,
            minutes INTEGER,
            direction TEXT,
            color TEXT,
            length INTEGER,
            bike_flag INTEGER,
            delay INTEGER,
            timestamp DATETIME,
            date DATE
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS daily_stats (
            date DATE PRIMARY KEY,
            total_departures INTEGER,
            total_delays INTEGER,
            avg_delay_minutes REAL
        )
    ''')
    
    conn.commit()
    conn.close()

def store_in_sqlite(transformed_data):
    """Store data in SQLite database"""
    db_path = os.environ.get('DATABASE_PATH', 'data/bart_history.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    now = datetime.now()
    date = now.date()
    
    for data in transformed_data:
        c.execute('''
            INSERT INTO departures (
                station, destination, platform, minutes, direction,
                color, length, bike_flag, delay, timestamp, date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['station'],
            data['destination'],
            data['platform'],
            data['minutes'],
            data['direction'],
            data['color'],
            data['length'],
            data['bike_flag'],
            data['delay'],
            now,
            date
        ))
    
    conn.commit()
    conn.close()

def run_etl_job():
    """
    Run the BART ETL job once and exit.
    This version is designed for GitHub Actions.
    """
    try:
        # Initialize components
        extractor = BartDataExtractor()
        transformer = BartDataTransformer()
        
        # Initialize SQLite database
        init_sqlite_db()

        # Extract station data
        logger.info("Extracting station data...")
        stations = extractor.get_stations()
        
        # Process each station
        for station in stations:
            try:
                # Extract departures
                logger.info(f"Processing station: {station['name']}")
                departures = extractor.get_departures(station['station_id'])
                
                # Transform data
                transformed_data = transformer.transform_departures(departures)
                
                # Store in SQLite
                store_in_sqlite(transformed_data)
                
                logger.info(f"Successfully processed station: {station['name']}")
                
            except Exception as e:
                logger.error(f"Error processing station {station['name']}: {str(e)}")
                continue

        logger.info("ETL job completed successfully")
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "processed_stations": len(stations)
        }
        
    except Exception as e:
        logger.error(f"ETL job failed: {str(e)}")
        return {
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

if __name__ == "__main__":
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Run the ETL job
    result = run_etl_job()
    print(result) 