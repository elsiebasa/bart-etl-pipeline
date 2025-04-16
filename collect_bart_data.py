import requests
import time
from datetime import datetime
from bigquery_store import BARTBigQueryStore
import os

class BARTDataCollector:
    def __init__(self, project_id):
        self.bart_api_key = 'MW9S-E7SL-26DU-VV8V'
        self.bart_api_base = 'http://api.bart.gov/api'
        self.bigquery_store = BARTBigQueryStore(project_id)
        
    def get_stations(self):
        """Get list of all BART stations"""
        response = requests.get(f'{self.bart_api_base}/stn.aspx', params={
            'cmd': 'stns',
            'key': self.bart_api_key,
            'json': 'y'
        })
        
        if response.status_code == 200:
            data = response.json()
            return data['root']['stations']['station']
        return []

    def get_departures(self, station_abbr):
        """Get departures for a specific station"""
        response = requests.get(f'{self.bart_api_base}/etd.aspx', params={
            'cmd': 'etd',
            'orig': station_abbr,
            'key': self.bart_api_key,
            'json': 'y'
        })
        
        if response.status_code == 200:
            data = response.json()
            return data['root']['station'][0] if 'station' in data['root'] else None
        return None

    def collect_and_store_data(self, interval_minutes=5):
        """Collect data from all stations and store in BigQuery"""
        print(f"Starting data collection at {datetime.now()}")
        
        while True:
            try:
                stations = self.get_stations()
                print(f"Found {len(stations)} stations")
                
                for station in stations:
                    station_name = station['name']
                    station_abbr = station['abbr']
                    print(f"Collecting data for {station_name} ({station_abbr})")
                    
                    station_data = self.get_departures(station_abbr)
                    if station_data and 'etd' in station_data:
                        for etd in station_data['etd']:
                            destination = etd['destination']
                            for estimate in etd['estimate']:
                                departure_data = {
                                    "station": station_name,
                                    "destination": destination,
                                    "platform": estimate['platform'],
                                    "minutes": int(estimate['minutes']) if estimate['minutes'].isdigit() else 0,
                                    "direction": estimate['direction'],
                                    "color": estimate['color'],
                                    "length": int(estimate['length']),
                                    "bike_flag": estimate['bikeflag'] == '1',
                                    "delay": int(estimate.get('delay', '0'))
                                }
                                self.bigquery_store.store_departure(departure_data)
                
                print(f"Data collection completed at {datetime.now()}")
                print(f"Waiting {interval_minutes} minutes before next collection...")
                time.sleep(interval_minutes * 60)
                
            except Exception as e:
                print(f"Error during data collection: {e}")
                time.sleep(60)  # Wait a minute before retrying

if __name__ == '__main__':
    # Get project ID from environment variable
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    if not project_id:
        raise ValueError("Please set GOOGLE_CLOUD_PROJECT environment variable")
    
    collector = BARTDataCollector(project_id)
    collector.collect_and_store_data() 