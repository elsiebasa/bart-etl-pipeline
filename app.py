from flask import Flask, jsonify
from flask_cors import CORS
import requests
from datetime import datetime
import os
import logging
from google.cloud import bigquery

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# BART API configuration
BART_API_KEY = 'MW9S-E7SL-26DU-VV8V'  # Public test key
BART_API_BASE = 'http://api.bart.gov/api'

# Initialize BigQuery client
client = bigquery.Client()

@app.route('/api/stations')
def get_stations():
    """
    Returns a list of all BART stations from the BART API.
    """
    try:
        logger.debug("Attempting to fetch stations from BART API")
        response = requests.get(f'{BART_API_BASE}/stn.aspx', params={
            'cmd': 'stns',
            'key': BART_API_KEY,
            'json': 'y'
        })
        
        logger.debug(f"BART API response status: {response.status_code}")
        logger.debug(f"BART API response content: {response.text[:200]}...")  # Log first 200 chars
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch stations. Status code: {response.status_code}")
            return jsonify({
                'status': 'error',
                'message': 'Failed to fetch stations from BART API'
            }), 500
            
        data = response.json()
        stations = [station['name'] for station in data['root']['stations']['station']]
        logger.debug(f"Successfully fetched {len(stations)} stations")
        return jsonify(stations)

    except Exception as e:
        logger.error(f"Error in get_stations: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/departures/<station>')
def get_departures(station):
    """
    Returns real-time departure data for a specific station from the BART API.
    """
    try:
        # First get the station abbreviation
        stations_response = requests.get(f'{BART_API_BASE}/stn.aspx', params={
            'cmd': 'stns',
            'key': BART_API_KEY,
            'json': 'y'
        })
        
        if stations_response.status_code != 200:
            return jsonify({
                'status': 'error',
                'message': 'Failed to fetch station information'
            }), 500
            
        stations_data = stations_response.json()
        station_abbr = None
        
        for s in stations_data['root']['stations']['station']:
            if s['name'].lower() == station.lower():
                station_abbr = s['abbr']
                break
                
        if not station_abbr:
            return jsonify({
                'status': 'error',
                'message': f'Station {station} not found'
            }), 404
            
        # Get departures for the station
        response = requests.get(f'{BART_API_BASE}/etd.aspx', params={
            'cmd': 'etd',
            'orig': station_abbr,
            'key': BART_API_KEY,
            'json': 'y'
        })
        
        if response.status_code != 200:
            return jsonify({
                'status': 'error',
                'message': 'Failed to fetch departures from BART API'
            }), 500
            
        data = response.json()
        departures = []
        
        if 'station' in data['root'] and data['root']['station']:
            station = data['root']['station'][0]
            if 'etd' in station:
                for etd in station['etd']:
                    for dest in etd['destination']:
                        for estimate in dest['estimate']:
                            departure = {
                                'destination': etd['destination'],
                                'direction': estimate['direction'],
                                'minutes': int(estimate['minutes']),
                                'platform': estimate['platform'],
                                'bike_flag': estimate['bikeflag'] == '1',
                                'delay': int(estimate.get('delay', '0')),
                                'color': estimate['color'],
                                'length': int(estimate['length'])
                            }
                            departures.append(departure)
        
        return jsonify({
            'status': 'success',
            'count': len(departures),
            'data': departures
        })

    except Exception as e:
        logger.error(f"Error in get_departures: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# Analytics endpoints
@app.route('/api/analytics/daily')
def get_daily_stats():
    """Get daily statistics from BigQuery"""
    try:
        days = request.args.get('days', default=7, type=int)
        query = f"""
        SELECT
            DATE(timestamp) as date,
            station,
            COUNT(*) as total_departures,
            SUM(CASE WHEN delay > 0 THEN 1 ELSE 0 END) as total_delays,
            AVG(CASE WHEN delay > 0 THEN delay ELSE NULL END) as avg_delay_minutes
        FROM `bart_data.departures`
        WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
        GROUP BY date, station
        ORDER BY date DESC, station
        """
        
        query_job = client.query(query)
        results = [dict(row.items()) for row in query_job]
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/delays')
def get_delay_patterns():
    """Get delay patterns from BigQuery"""
    try:
        days = request.args.get('days', default=7, type=int)
        query = f"""
        SELECT
            DATE(timestamp) as date,
            HOUR(timestamp) as hour,
            station,
            AVG(delay) as avg_delay,
            COUNT(*) as total_trains
        FROM `bart_data.departures`
        WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
        AND delay > 0
        GROUP BY date, hour, station
        ORDER BY date DESC, hour
        """
        
        query_job = client.query(query)
        results = [dict(row.items()) for row in query_job]
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/station')
def get_station_stats():
    """Get statistics for a specific station"""
    try:
        station = request.args.get('station')
        days = request.args.get('days', default=7, type=int)
        
        if not station:
            return jsonify({'error': 'Station parameter is required'}), 400
            
        query = f"""
        SELECT
            destination,
            COUNT(*) as total_departures,
            AVG(CASE WHEN delay > 0 THEN delay ELSE NULL END) as avg_delay_minutes,
            COUNT(CASE WHEN delay > 0 THEN 1 END) as delay_count
        FROM `bart_data.departures`
        WHERE station = @station
        AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
        GROUP BY destination
        ORDER BY total_departures DESC
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("station", "STRING", station),
            ]
        )
        
        query_job = client.query(query, job_config=job_config)
        results = [dict(row.items()) for row in query_job]
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting Flask server on port {port}")
    app.run(host='127.0.0.1', port=port, debug=True) 