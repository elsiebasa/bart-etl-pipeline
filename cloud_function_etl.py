import os
import json
import logging
from datetime import datetime
import functions_framework
from google.cloud import bigquery

# Import your ETL modules
from etl.extract import BartDataExtractor
from etl.transform import BartDataTransformer
from etl.load import BartDataLoader

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@functions_framework.http
def run_bart_etl(request):
    """
    Cloud Function to run the BART ETL job.
    This function will be triggered by Cloud Scheduler.
    """
    try:
        logger.info("Starting BART ETL job")
        start_time = datetime.now()
        
        # Initialize ETL components
        extractor = BartDataExtractor()
        transformer = BartDataTransformer()
        loader = BartDataLoader()
        
        # 1. Extract and load stations (daily)
        logger.info("Extracting station data")
        stations = extractor.get_stations()
        cleaned_stations = transformer.clean_station_data(stations)
        loader.load_stations(cleaned_stations)
        
        # 2. Extract and load departures for all stations
        logger.info("Extracting departure data for all stations")
        all_departures = []
        
        for station in stations:
            try:
                logger.info(f"Processing station {station['station_id']}")
                departures = extractor.get_departures(station['station_id'])
                cleaned_departures = transformer.clean_departure_data(departures)
                all_departures.extend(cleaned_departures)
                loader.load_departures(cleaned_departures)
            except Exception as e:
                logger.error(f"Error processing station {station['station_id']}: {str(e)}")
                continue
        
        # 3. Calculate and load metrics
        if all_departures:
            logger.info("Calculating metrics")
            metrics = transformer.calculate_metrics(all_departures)
            loader.load_metrics(metrics)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.info(f"ETL job completed in {duration:.2f} seconds")
        
        return {
            'status': 'success',
            'message': f'ETL job completed in {duration:.2f} seconds',
            'stations_processed': len(stations),
            'departures_processed': len(all_departures)
        }
        
    except Exception as e:
        logger.error(f"Error in ETL job: {str(e)}")
        return {
            'status': 'error',
            'message': str(e)
        } 