import logging
from typing import Dict, List
from datetime import datetime, timezone
import pandas as pd
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BartDataTransformer:
    """Handles transformation and cleaning of BART data"""
    
    def __init__(self):
        self.valid_directions = {'North', 'South', 'East', 'West'}
        self.valid_line_colors = {'RED', 'BLUE', 'GREEN', 'YELLOW', 'ORANGE'}
    
    def clean_station_data(self, stations: List[Dict]) -> List[Dict]:
        """Clean and validate station data"""
        try:
            cleaned_stations = []
            for station in stations:
                # Convert to DataFrame for easier cleaning
                df = pd.DataFrame([station])
                
                # Clean string fields
                string_columns = ['station_id', 'name', 'address', 'city', 'county', 'state', 'zipcode']
                for col in string_columns:
                    if col in df:
                        df[col] = df[col].str.strip()
                
                # Validate coordinates
                if 'latitude' in df and 'longitude' in df:
                    # San Francisco Bay Area bounds
                    df = df[
                        (df['latitude'].between(37.0, 39.0)) & 
                        (df['longitude'].between(-123.0, -121.0))
                    ]
                
                # Convert back to dict
                if not df.empty:
                    cleaned_stations.append(df.to_dict('records')[0])
            
            logger.info(f"Successfully cleaned {len(cleaned_stations)} stations")
            return cleaned_stations
            
        except Exception as e:
            logger.error(f"Error cleaning station data: {str(e)}")
            raise
    
    def clean_departure_data(self, departures: List[Dict]) -> List[Dict]:
        """Clean and validate departure data"""
        try:
            cleaned_departures = []
            for departure in departures:
                # Convert to DataFrame for easier cleaning
                df = pd.DataFrame([departure])
                
                # Clean and validate minutes
                if 'minutes' in df:
                    df['minutes'] = pd.to_numeric(df['minutes'], errors='coerce')
                    df = df[df['minutes'].between(0, 120)]  # Remove unrealistic values
                
                # Clean and validate delay
                if 'delay' in df:
                    df['delay'] = pd.to_numeric(df['delay'], errors='coerce').fillna(0)
                    df = df[df['delay'].between(0, 60)]  # Remove unrealistic delays
                
                # Validate direction
                if 'direction' in df:
                    df = df[df['direction'].isin(self.valid_directions)]
                
                # Validate line color
                if 'line_color' in df:
                    df['line_color'] = df['line_color'].str.upper()
                    df = df[df['line_color'].isin(self.valid_line_colors)]
                
                # Validate platform
                if 'platform' in df:
                    df['platform'] = pd.to_numeric(df['platform'], errors='coerce')
                    df = df[df['platform'].between(1, 4)]
                
                # Convert back to dict
                if not df.empty:
                    cleaned_departures.append(df.to_dict('records')[0])
            
            logger.info(f"Successfully cleaned {len(cleaned_departures)} departures")
            return cleaned_departures
            
        except Exception as e:
            logger.error(f"Error cleaning departure data: {str(e)}")
            raise
    
    def calculate_metrics(self, departures: List[Dict]) -> Dict:
        """Calculate various metrics from departure data"""
        try:
            df = pd.DataFrame(departures)
            
            metrics = {
                'total_departures': len(df),
                'avg_delay': df['delay'].mean(),
                'max_delay': df['delay'].max(),
                'delayed_trains': len(df[df['delay'] > 0]),
                'delay_rate': len(df[df['delay'] > 0]) / len(df) if len(df) > 0 else 0,
                'bikes_allowed_rate': df['bikes_allowed'].mean() if 'bikes_allowed' in df else None,
                'avg_train_length': df['length'].mean() if 'length' in df else None,
                'calculated_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Calculate metrics by direction if available
            if 'direction' in df:
                metrics['direction_counts'] = df['direction'].value_counts().to_dict()
            
            logger.info("Successfully calculated metrics")
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating metrics: {str(e)}")
            raise

if __name__ == "__main__":
    # Test the transformer
    from extract import BartDataExtractor
    
    extractor = BartDataExtractor()
    transformer = BartDataTransformer()
    
    # Test station data transformation
    stations = extractor.get_stations()
    cleaned_stations = transformer.clean_station_data(stations)
    print(f"\nCleaned {len(cleaned_stations)} stations")
    print("Sample cleaned station:", cleaned_stations[0])
    
    # Test departure data transformation
    if stations:
        departures = extractor.get_departures(stations[0]['station_id'])
        cleaned_departures = transformer.clean_departure_data(departures)
        print(f"\nCleaned {len(cleaned_departures)} departures")
        if cleaned_departures:
            print("Sample cleaned departure:", cleaned_departures[0])
        
        # Test metrics calculation
        metrics = transformer.calculate_metrics(cleaned_departures)
        print("\nCalculated metrics:", metrics) 