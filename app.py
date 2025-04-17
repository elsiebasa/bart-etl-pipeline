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
            s.name,
            s.abbr,
            ds.date,
            ds.total_departures,
            ds.delayed_departures,
            ds.avg_delay_minutes,
            ds.max_delay_minutes
        FROM daily_stats ds
        JOIN stations s ON ds.station_id = s.id
        WHERE ds.date >= date('now', '-7 days')
        ORDER BY s.name, ds.date DESC
        ''')
        
        stats = cursor.fetchall()
        db.close()
        
        # Format the data
        analytics = []
        for stat in stats:
            analytics.append({
                'station_name': stat[0],
                'station_id': stat[1],
                'date': stat[2],
                'total_departures': stat[3],
                'delayed_departures': stat[4],
                'avg_delay_minutes': stat[5],
                'max_delay_minutes': stat[6]
            })
        
        return jsonify({
            "status": "Data available",
            "timestamp": datetime.now().isoformat(),
            "data": analytics
        })
        
    except Exception as e:
        return jsonify({
            "status": "Error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "data": []
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 