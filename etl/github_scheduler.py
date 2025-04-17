import requests
from datetime import datetime
import logging
from database import BartDatabase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# BART API configuration
BART_API_KEY = 'MW9S-E7SL-26DU-VV8V'  # Public test key
BART_API_BASE_URL = 'http://api.bart.gov/api'

def get_stations():
    """Fetch all BART stations"""
    try:
        response = requests.get(f'{BART_API_BASE_URL}/stn.aspx', params={
            'cmd': 'stns',
            'key': BART_API_KEY,
            'json': 'y'
        })
        response.raise_for_status()
        data = response.json()
        
        stations = []
        for station in data['root']['stations']['station']:
            stations.append({
                'id': station['abbr'],
                'name': station['name'],
                'abbr': station['abbr'],
                'city': station.get('city'),
                'county': station.get('county'),
                'state': station.get('state'),
                'zipcode': station.get('zipcode')
            })
        
        return stations
    except Exception as e:
        logger.error(f"Error fetching stations: {str(e)}")
        return []

def get_departures(station_id):
    """Fetch departures for a specific station"""
    try:
        response = requests.get(f'{BART_API_BASE_URL}/etd.aspx', params={
            'cmd': 'etd',
            'orig': station_id,
            'key': BART_API_KEY,
            'json': 'y'
        })
        response.raise_for_status()
        data = response.json()
        
        departures = []
        if 'root' in data and 'station' in data['root']:
            station_data = data['root']['station'][0]
            if 'etd' in station_data:
                for etd in station_data['etd']:
                    destination = etd['destination']
                    for estimate in etd['estimate']:
                        departure = {
                            'station_id': station_id,
                            'destination': destination,
                            'direction': estimate['direction'],
                            'minutes': int(estimate['minutes'] if estimate['minutes'] != 'Leaving' else '0'),
                            'platform': estimate['platform'],
                            'length': int(estimate['length']),
                            'color': estimate['color'],
                            'bikes': int(estimate['bikeflag'])
                        }
                        departures.append(departure)
        
        return departures
    except Exception as e:
        logger.error(f"Error fetching departures for station {station_id}: {str(e)}")
        return []

def main():
    """Main ETL process"""
    try:
        # Initialize database
        db = BartDatabase()
        
        # Get and save stations
        logger.info("Fetching stations...")
        stations = get_stations()
        for station in stations:
            db.save_station(station)
        logger.info(f"Saved {len(stations)} stations")
        
        # Get and save departures for each station
        today = datetime.now().strftime('%Y-%m-%d')
        for station in stations:
            logger.info(f"Processing station: {station['name']}")
            departures = get_departures(station['id'])
            
            for departure in departures:
                db.save_departure(departure)
            
            # Update daily stats
            db.update_daily_stats(station['id'], today)
            logger.info(f"Saved {len(departures)} departures for {station['name']}")
        
        db.close()
        logger.info("ETL process completed successfully")
        
    except Exception as e:
        logger.error(f"Error in ETL process: {str(e)}")
        raise

if __name__ == '__main__':
    main() 