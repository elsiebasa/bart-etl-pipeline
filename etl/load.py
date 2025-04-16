import os
import logging
from datetime import datetime
from google.cloud import bigquery

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BartDataLoader:
    """Loader for BART data into BigQuery"""
    
    def __init__(self):
        """Initialize the loader with BigQuery client"""
        self.client = bigquery.Client()
        self.project_id = "baet-de-project"  # Your project ID
        self.dataset_id = "bart_data"        # Your dataset ID
        
        # Table IDs
        self.stations_table_id = f"{self.project_id}.{self.dataset_id}.stations"
        self.departures_table_id = f"{self.project_id}.{self.dataset_id}.departures"
        self.metrics_table_id = f"{self.project_id}.{self.dataset_id}.metrics"
    
    def load_stations(self, stations):
        """Load station data into BigQuery"""
        if not stations:
            logger.warning("No station data to load")
            return
        
        try:
            # Prepare data for BigQuery
            rows_to_insert = []
            for station in stations:
                rows_to_insert.append({
                    'station_id': station.get('station_id'),
                    'name': station.get('name'),
                    'abbr': station.get('abbr'),
                    'latitude': station.get('latitude'),
                    'longitude': station.get('longitude')
                })
            
            # Load data into BigQuery
            errors = self.client.insert_rows_json(
                self.stations_table_id, 
                rows_to_insert
            )
            
            if errors:
                logger.error(f"Errors loading stations: {errors}")
            else:
                logger.info(f"Loaded {len(rows_to_insert)} stations into BigQuery")
                
        except Exception as e:
            logger.error(f"Error loading stations: {str(e)}")
    
    def load_departures(self, departures):
        """Load departure data into BigQuery"""
        if not departures:
            logger.warning("No departure data to load")
            return
        
        try:
            # Prepare data for BigQuery
            rows_to_insert = []
            for departure in departures:
                # Map to match your existing schema
                rows_to_insert.append({
                    'timestamp': departure.get('timestamp', datetime.now()),
                    'station': departure.get('station_id'),
                    'destination': departure.get('destination'),
                    'minutes': departure.get('estimated_minutes'),
                    'platform': departure.get('platform'),
                    'direction': departure.get('direction'),
                    'delay': departure.get('delay'),
                    'length': departure.get('length')
                })
            
            # Load data into BigQuery
            errors = self.client.insert_rows_json(
                self.departures_table_id, 
                rows_to_insert
            )
            
            if errors:
                logger.error(f"Errors loading departures: {errors}")
            else:
                logger.info(f"Loaded {len(rows_to_insert)} departures into BigQuery")
                
        except Exception as e:
            logger.error(f"Error loading departures: {str(e)}")
    
    def load_metrics(self, metrics):
        """Load metrics data into BigQuery"""
        if not metrics:
            logger.warning("No metrics data to load")
            return
        
        try:
            # Prepare data for BigQuery
            rows_to_insert = []
            for metric in metrics:
                rows_to_insert.append({
                    'date': metric.get('date'),
                    'total_trains': metric.get('total_trains'),
                    'avg_delay': metric.get('avg_delay'),
                    'delayed_trains': metric.get('delayed_trains')
                })
            
            # Load data into BigQuery
            errors = self.client.insert_rows_json(
                self.metrics_table_id, 
                rows_to_insert
            )
            
            if errors:
                logger.error(f"Errors loading metrics: {errors}")
            else:
                logger.info(f"Loaded {len(rows_to_insert)} metrics into BigQuery")
                
        except Exception as e:
            logger.error(f"Error loading metrics: {str(e)}")

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