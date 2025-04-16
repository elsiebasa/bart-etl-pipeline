import sqlite3
import logging
from typing import Dict, List
from datetime import datetime, timezone
import json
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BartDataLoader:
    """Handles loading BART data into SQLite database"""
    
    def __init__(self, db_path: str = 'data/bart.db'):
        """Initialize loader with database path"""
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._create_tables()
    
    def _create_tables(self):
        """Create necessary database tables if they don't exist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create stations table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS stations (
                    station_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    latitude REAL,
                    longitude REAL,
                    address TEXT,
                    city TEXT,
                    county TEXT,
                    state TEXT,
                    zipcode TEXT,
                    extracted_at TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                ''')
                
                # Create departures table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS departures (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    station_id TEXT,
                    destination TEXT,
                    direction TEXT,
                    minutes INTEGER,
                    platform TEXT,
                    line_color TEXT,
                    length INTEGER,
                    bikes_allowed BOOLEAN,
                    delay INTEGER,
                    extracted_at TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (station_id) REFERENCES stations(station_id)
                )
                ''')
                
                # Create metrics table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    total_departures INTEGER,
                    avg_delay REAL,
                    max_delay INTEGER,
                    delayed_trains INTEGER,
                    delay_rate REAL,
                    bikes_allowed_rate REAL,
                    avg_train_length REAL,
                    direction_counts TEXT,
                    calculated_at TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                ''')
                
                # Create indexes
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_departures_station ON departures(station_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_departures_time ON departures(extracted_at)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_time ON metrics(calculated_at)')
                
                conn.commit()
                logger.info("Successfully created database tables")
                
        except Exception as e:
            logger.error(f"Error creating database tables: {str(e)}")
            raise
    
    def load_stations(self, stations: List[Dict]):
        """Load station data into database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for station in stations:
                    cursor.execute('''
                    INSERT OR REPLACE INTO stations (
                        station_id, name, latitude, longitude,
                        address, city, county, state, zipcode, extracted_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        station['station_id'],
                        station['name'],
                        station['latitude'],
                        station['longitude'],
                        station['address'],
                        station['city'],
                        station['county'],
                        station['state'],
                        station['zipcode'],
                        station['extracted_at']
                    ))
                
                conn.commit()
                logger.info(f"Successfully loaded {len(stations)} stations")
                
        except Exception as e:
            logger.error(f"Error loading station data: {str(e)}")
            raise
    
    def load_departures(self, departures: List[Dict]):
        """Load departure data into database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for departure in departures:
                    cursor.execute('''
                    INSERT INTO departures (
                        station_id, destination, direction, minutes,
                        platform, line_color, length, bikes_allowed,
                        delay, extracted_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        departure['station_id'],
                        departure['destination'],
                        departure['direction'],
                        departure['minutes'],
                        departure['platform'],
                        departure['line_color'],
                        departure['length'],
                        departure['bikes_allowed'],
                        departure['delay'],
                        departure['extracted_at']
                    ))
                
                conn.commit()
                logger.info(f"Successfully loaded {len(departures)} departures")
                
        except Exception as e:
            logger.error(f"Error loading departure data: {str(e)}")
            raise
    
    def load_metrics(self, metrics: Dict):
        """Load metrics data into database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Convert direction_counts to JSON string if it exists
                direction_counts = json.dumps(metrics.get('direction_counts', {}))
                
                cursor.execute('''
                INSERT INTO metrics (
                    total_departures, avg_delay, max_delay,
                    delayed_trains, delay_rate, bikes_allowed_rate,
                    avg_train_length, direction_counts, calculated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    metrics['total_departures'],
                    metrics['avg_delay'],
                    metrics['max_delay'],
                    metrics['delayed_trains'],
                    metrics['delay_rate'],
                    metrics['bikes_allowed_rate'],
                    metrics['avg_train_length'],
                    direction_counts,
                    metrics['calculated_at']
                ))
                
                conn.commit()
                logger.info("Successfully loaded metrics")
                
        except Exception as e:
            logger.error(f"Error loading metrics: {str(e)}")
            raise

if __name__ == "__main__":
    # Test the loader
    from extract import BartDataExtractor
    from transform import BartDataTransformer
    
    extractor = BartDataExtractor()
    transformer = BartDataTransformer()
    loader = BartDataLoader()
    
    # Test full ETL pipeline
    # 1. Extract and load stations
    stations = extractor.get_stations()
    cleaned_stations = transformer.clean_station_data(stations)
    loader.load_stations(cleaned_stations)
    
    # 2. Extract and load departures for first station
    if cleaned_stations:
        departures = extractor.get_departures(cleaned_stations[0]['station_id'])
        cleaned_departures = transformer.clean_departure_data(departures)
        loader.load_departures(cleaned_departures)
        
        # 3. Calculate and load metrics
        metrics = transformer.calculate_metrics(cleaned_departures)
        loader.load_metrics(metrics)
        
    print("\nETL pipeline test completed successfully!") 