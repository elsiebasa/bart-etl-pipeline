import requests
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BartDataExtractor:
    """Handles extraction of data from BART API"""
    
    def __init__(self):
        self.API_KEY = 'MW9S-E7SL-26DU-VV8V'  # Public test key
        self.BASE_URL = 'http://api.bart.gov/api'
        
    def get_stations(self) -> List[Dict]:
        """Extract station data from BART API"""
        try:
            response = requests.get(
                f'{self.BASE_URL}/stn.aspx',
                params={
                    'cmd': 'stns',
                    'key': self.API_KEY,
                    'json': 'y'
                }
            )
            response.raise_for_status()
            data = response.json()
            
            stations = []
            for station in data['root']['stations']['station']:
                stations.append({
                    'station_id': station['abbr'],
                    'name': station['name'],
                    'latitude': float(station['gtfs_latitude']),
                    'longitude': float(station['gtfs_longitude']),
                    'address': station['address'],
                    'city': station['city'],
                    'county': station['county'],
                    'state': station['state'],
                    'zipcode': station['zipcode'],
                    'extracted_at': datetime.now(timezone.utc).isoformat()
                })
            
            logger.info(f"Successfully extracted {len(stations)} stations")
            return stations
            
        except Exception as e:
            logger.error(f"Error extracting station data: {str(e)}")
            raise
    
    def get_departures(self, station_id: str) -> List[Dict]:
        """Extract real-time departure data for a station"""
        try:
            response = requests.get(
                f'{self.BASE_URL}/etd.aspx',
                params={
                    'cmd': 'etd',
                    'orig': station_id,
                    'key': self.API_KEY,
                    'json': 'y'
                }
            )
            response.raise_for_status()
            data = response.json()
            
            departures = []
            extracted_at = datetime.now(timezone.utc)
            
            if 'station' in data['root'] and data['root']['station']:
                station = data['root']['station'][0]
                if 'etd' in station:
                    for etd in station['etd']:
                        for estimate in etd['estimate']:
                            departures.append({
                                'station_id': station_id,
                                'destination': etd['destination'],
                                'direction': estimate['direction'],
                                'minutes': int(estimate['minutes']) if estimate['minutes'].isdigit() else None,
                                'platform': estimate['platform'],
                                'line_color': estimate['color'],
                                'length': int(estimate['length']),
                                'bikes_allowed': estimate['bikeflag'] == '1',
                                'delay': int(estimate.get('delay', '0')),
                                'extracted_at': extracted_at.isoformat()
                            })
            
            logger.info(f"Successfully extracted {len(departures)} departures for station {station_id}")
            return departures
            
        except Exception as e:
            logger.error(f"Error extracting departure data for station {station_id}: {str(e)}")
            raise

if __name__ == "__main__":
    # Test the extractor
    extractor = BartDataExtractor()
    
    # Test station extraction
    stations = extractor.get_stations()
    print(f"\nExtracted {len(stations)} stations")
    print("Sample station:", stations[0])
    
    # Test departure extraction for first station
    if stations:
        departures = extractor.get_departures(stations[0]['station_id'])
        print(f"\nExtracted {len(departures)} departures")
        if departures:
            print("Sample departure:", departures[0]) 