import requests
import json
from pprint import pprint

# BART API configuration
BART_API_KEY = 'MW9S-E7SL-26DU-VV8V'  # Public test key
BART_API_BASE = 'http://api.bart.gov/api'

def test_stations():
    """Test the stations endpoint"""
    print("\n=== Testing Stations API ===")
    response = requests.get(f'{BART_API_BASE}/stn.aspx', params={
        'cmd': 'stns',
        'key': BART_API_KEY,
        'json': 'y'
    })
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        stations = data['root']['stations']['station']
        print(f"\nFound {len(stations)} stations:")
        for station in stations[:5]:  # Show first 5 stations
            print(f"- {station['name']} ({station['abbr']})")
    else:
        print("Failed to get stations")
        print(response.text)

def test_departures(station_abbr='12TH'):
    """Test the departures endpoint for a specific station"""
    print(f"\n=== Testing Departures API for {station_abbr} ===")
    response = requests.get(f'{BART_API_BASE}/etd.aspx', params={
        'cmd': 'etd',
        'orig': station_abbr,
        'key': BART_API_KEY,
        'json': 'y'
    })
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if 'station' in data['root'] and data['root']['station']:
            station = data['root']['station'][0]
            print(f"\nStation: {station['name']}")
            if 'etd' in station:
                for etd in station['etd']:
                    print(f"\nDestination: {etd['destination']}")
                    for estimate in etd['estimate']:
                        print(f"  Platform {estimate['platform']}:")
                        print(f"    {estimate['minutes']} min - {estimate['direction']} bound")
                        print(f"    Color: {estimate['color']}")
                        print(f"    Length: {estimate['length']} cars")
                        print(f"    Delay: {estimate['delay']} min")
                        print(f"    Bikes allowed: {'Yes' if estimate['bikeflag'] == '1' else 'No'}")
    else:
        print("Failed to get departures")
        print(response.text)

if __name__ == '__main__':
    print("Testing BART API...")
    test_stations()
    test_departures() 