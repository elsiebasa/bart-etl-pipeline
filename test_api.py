import requests
from pprint import pprint

def test_bart_api():
    # BART API configuration
    BART_API_KEY = 'MW9S-E7SL-26DU-VV8V'
    BART_API_BASE = 'http://api.bart.gov/api'
    
    # Test stations endpoint
    print("\n=== Testing BART API stations endpoint ===")
    response = requests.get(f'{BART_API_BASE}/stn.aspx', params={
        'cmd': 'stns',
        'key': BART_API_KEY,
        'json': 'y'
    })
    
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        stations = data['root']['stations']['station']
        print(f"\nFound {len(stations)} stations. First 5 stations:")
        for station in stations[:5]:
            print(f"- {station['name']} ({station['abbr']})")
    else:
        print("Failed to fetch stations")

    # Test departures endpoint for 12th St Oakland
    print("\n=== Testing BART API departures endpoint ===")
    station_abbr = '12TH'  # 12th St Oakland
    response = requests.get(f'{BART_API_BASE}/etd.aspx', params={
        'cmd': 'etd',
        'orig': station_abbr,
        'key': BART_API_KEY,
        'json': 'y'
    })
    
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("\nRaw API Response:")
        pprint(data)
        
        if 'station' in data['root'] and data['root']['station']:
            station = data['root']['station'][0]
            print(f"\nStation: {station.get('name', 'Unknown')}")
            
            if 'etd' in station:
                print("\nDepartures:")
                for etd in station['etd']:
                    destination = etd['destination']
                    print(f"\nTo: {destination}")
                    for estimate in etd['estimate']:
                        print(f"- Platform {estimate['platform']}: {estimate['minutes']} min")
                        print(f"  Direction: {estimate['direction']}")
                        print(f"  Length: {estimate['length']} cars")
                        print(f"  Color: {estimate['color']}")
                        print(f"  Bike Flag: {estimate['bikeflag']}")
                        if 'delay' in estimate:
                            print(f"  Delay: {estimate['delay']} min")
    else:
        print("Failed to fetch departures")

if __name__ == '__main__':
    test_bart_api() 