import schedule
import time
import logging
from datetime import datetime, timezone
import os
from typing import List, Dict
import signal
import sys
import json

from extract import BartDataExtractor
from transform import BartDataTransformer
from load import BartDataLoader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/bart_etl.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BartETLScheduler:
    """Scheduler for BART ETL pipeline"""
    
    def __init__(self):
        self.extractor = BartDataExtractor()
        self.transformer = BartDataTransformer()
        self.loader = BartDataLoader()
        self.running = True
        self.checkpoint_file = 'data/etl_checkpoint.json'
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGTERM, self.handle_shutdown)
    
    def handle_shutdown(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info("Received shutdown signal. Stopping scheduler...")
        self.running = False
        self.save_checkpoint()
    
    def save_checkpoint(self):
        """Save current state to checkpoint file"""
        try:
            checkpoint = {
                'last_run': datetime.now(timezone.utc).isoformat(),
                'last_station_index': getattr(self, 'last_station_index', 0),
                'stations_processed': getattr(self, 'stations_processed', []),
                'all_departures_count': getattr(self, 'all_departures_count', 0)
            }
            
            os.makedirs(os.path.dirname(self.checkpoint_file), exist_ok=True)
            with open(self.checkpoint_file, 'w') as f:
                json.dump(checkpoint, f)
                
            logger.info(f"Checkpoint saved: {checkpoint}")
        except Exception as e:
            logger.error(f"Error saving checkpoint: {str(e)}")
    
    def load_checkpoint(self):
        """Load state from checkpoint file"""
        try:
            if os.path.exists(self.checkpoint_file):
                with open(self.checkpoint_file, 'r') as f:
                    checkpoint = json.load(f)
                
                self.last_run = datetime.fromisoformat(checkpoint['last_run'])
                self.last_station_index = checkpoint.get('last_station_index', 0)
                self.stations_processed = checkpoint.get('stations_processed', [])
                self.all_departures_count = checkpoint.get('all_departures_count', 0)
                
                logger.info(f"Checkpoint loaded: {checkpoint}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error loading checkpoint: {str(e)}")
            return False
    
    def run_etl_job(self):
        """Run one complete ETL job"""
        try:
            logger.info("Starting ETL job")
            start_time = time.time()
            
            # 1. Extract and load stations (daily)
            if datetime.now().hour == 0:  # Run once per day at midnight
                logger.info("Running station update")
                stations = self.extractor.get_stations()
                cleaned_stations = self.transformer.clean_station_data(stations)
                self.loader.load_stations(cleaned_stations)
                self.stations_processed = []
                self.last_station_index = 0
            
            # 2. Extract and load departures for all stations
            stations = self.extractor.get_stations()
            all_departures = []
            
            # Resume from last processed station if available
            if hasattr(self, 'last_station_index') and hasattr(self, 'stations_processed'):
                logger.info(f"Resuming from station index {self.last_station_index}")
                for i, station in enumerate(stations):
                    if i < self.last_station_index:
                        continue
                        
                    try:
                        logger.info(f"Processing station {station['station_id']} ({i+1}/{len(stations)})")
                        departures = self.extractor.get_departures(station['station_id'])
                        cleaned_departures = self.transformer.clean_departure_data(departures)
                        all_departures.extend(cleaned_departures)
                        self.loader.load_departures(cleaned_departures)
                        
                        self.last_station_index = i + 1
                        self.stations_processed.append(station['station_id'])
                        self.all_departures_count = len(all_departures)
                        
                        # Save checkpoint after each station
                        self.save_checkpoint()
                    except Exception as e:
                        logger.error(f"Error processing station {station['station_id']}: {str(e)}")
                        continue
            else:
                # First run - process all stations
                self.last_station_index = 0
                self.stations_processed = []
                self.all_departures_count = 0
                
                for i, station in enumerate(stations):
                    try:
                        logger.info(f"Processing station {station['station_id']} ({i+1}/{len(stations)})")
                        departures = self.extractor.get_departures(station['station_id'])
                        cleaned_departures = self.transformer.clean_departure_data(departures)
                        all_departures.extend(cleaned_departures)
                        self.loader.load_departures(cleaned_departures)
                        
                        self.last_station_index = i + 1
                        self.stations_processed.append(station['station_id'])
                        self.all_departures_count = len(all_departures)
                        
                        # Save checkpoint after each station
                        self.save_checkpoint()
                    except Exception as e:
                        logger.error(f"Error processing station {station['station_id']}: {str(e)}")
                        continue
            
            # 3. Calculate and load metrics
            if all_departures:
                metrics = self.transformer.calculate_metrics(all_departures)
                self.loader.load_metrics(metrics)
            
            duration = time.time() - start_time
            logger.info(f"ETL job completed in {duration:.2f} seconds")
            
            # Reset checkpoint after successful completion
            if os.path.exists(self.checkpoint_file):
                os.remove(self.checkpoint_file)
            
        except Exception as e:
            logger.error(f"Error in ETL job: {str(e)}")
            self.save_checkpoint()
    
    def start(self):
        """Start the scheduler"""
        logger.info("Starting BART ETL scheduler")
        
        # Try to load checkpoint
        self.load_checkpoint()
        
        # Schedule jobs
        schedule.every(1).minutes.do(self.run_etl_job)  # Run every minute
        
        # Run first job immediately
        self.run_etl_job()
        
        # Keep running until shutdown
        while self.running:
            schedule.run_pending()
            time.sleep(1)
        
        logger.info("Scheduler stopped")

if __name__ == "__main__":
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Start the scheduler
    scheduler = BartETLScheduler()
    scheduler.start() 