from flask import Flask, jsonify
from flask_cors import CORS
import requests
from datetime import datetime
from etl.database import BartDatabase

app = Flask(__name__)
CORS(app)

# BART API configuration
BART_API_KEY = 'MW9S-E7SL-26DU-VV8V'  # This is a public test key
BART_API_BASE_URL = 'http://api.bart.gov/api'

@app.route('/api/stations', methods=['GET'])
def get_stations():
    """Get list of BART stations"""
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
                'name': station['name'],
                'abbr': station['abbr']
            })
        
        return jsonify(stations)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/departures/<station>', methods=['GET'])
def get_departures(station):
    """Get real-time departures for a specific station"""
    try:
        response = requests.get(f'{BART_API_BASE_URL}/etd.aspx', params={
            'cmd': 'etd',
            'orig': station,
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
                            'timestamp': datetime.now().isoformat(),
                            'destination': destination,
                            'minutes': int(estimate['minutes'] if estimate['minutes'] != 'Leaving' else '0'),
                            'platform': estimate['platform'],
                            'direction': estimate['direction'],
                            'delay': 0,  # BART API doesn't provide delay info
                            'length': int(estimate['length'])
                        }
                        departures.append(departure)
        
        return jsonify({
            "status": "Data available",
            "timestamp": datetime.now().isoformat(),
            "departures": departures
        })
        
    except Exception as e:
        return jsonify({
            "status": "Error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "departures": []
        }), 500

@app.route('/api/analytics/daily', methods=['GET'])
def get_daily_analytics():
    """Get daily analytics for the past week"""
    # This endpoint would need to be modified to work with historical data
    # For now, returning empty analytics with status
    return jsonify({
        "status": "No historical data available",
        "timestamp": datetime.now().isoformat(),
        "data": []
    })

@app.route('/api/analytics/stations', methods=['GET'])
def get_station_analytics():
    """Get analytics by station"""
    try:
        db = BartDatabase()
        cursor = db.conn.cursor()
        
        # Get station stats for the last 7 days
        cursor.execute('''
        SELECT 
            d.destination,
            COUNT(*) as total_departures,
            COUNT(CASE WHEN d.delay != 0 THEN 1 END) as delayed_trains,
            ROUND(COALESCE(AVG(ABS(d.delay)), 0), 1) as avg_delay_minutes
        FROM departures d
        WHERE d.timestamp >= datetime('now', '-7 days')
        GROUP BY d.destination
        ORDER BY total_departures DESC
        ''')
        
        stats = cursor.fetchall()
        db.close()
        
        # Format the data
        analytics = []
        for stat in stats:
            analytics.append({
                'destination': stat[0] or 'Unknown',
                'total_departures': stat[1] or 0,
                'delayed_trains': stat[2] or 0,
                'avg_delay_minutes': float(stat[3] or 0)
            })
        
        # If no data found, return empty array with success status
        if not analytics:
            return jsonify({
                "status": "No data available",
                "timestamp": datetime.now().isoformat(),
                "data": []
            })
        
        return jsonify({
            "status": "Data available",
            "timestamp": datetime.now().isoformat(),
            "data": analytics
        })
        
    except Exception as e:
        print(f"Error in get_station_analytics: {str(e)}")  # Add logging
        return jsonify({
            "status": "Error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "data": []
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 