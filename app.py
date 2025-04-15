from flask import Flask, jsonify
from flask_cors import CORS
from google.cloud import bigquery
from google.oauth2 import service_account
from datetime import datetime, timedelta
import os
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def get_bigquery_client():
    """
    Authenticates and returns a BigQuery client using service account credentials.
    """
    try:
        # Check if we're running in production (Render.com)
        if os.environ.get('RENDER'):
            # In production, credentials are stored as an environment variable
            credentials_json = os.environ.get('GOOGLE_CREDENTIALS')
            if credentials_json:
                credentials_info = json.loads(credentials_json)
                credentials = service_account.Credentials.from_service_account_info(
                    credentials_info,
                    scopes=["https://www.googleapis.com/auth/cloud-platform"],
                )
            else:
                raise ValueError("GOOGLE_CREDENTIALS environment variable not set")
        else:
            # In development, use the service account key file
            credentials = service_account.Credentials.from_service_account_file(
                'service-account-key.json',
                scopes=["https://www.googleapis.com/auth/cloud-platform"],
            )
        
        client = bigquery.Client(credentials=credentials, project=credentials.project_id)
        return client
    except Exception as e:
        print(f"Error connecting to BigQuery: {e}")
        return None

@app.route('/api/stations')
def get_stations():
    """
    Returns a list of all BART stations.
    """
    try:
        # Initialize BigQuery client
        client = get_bigquery_client()
        if client is None:
            return jsonify({'error': 'Failed to connect to BigQuery'}), 500

        # Construct the query to get unique stations
        query = """
            SELECT DISTINCT station
            FROM `bart_data.etd_data`
            ORDER BY station
        """

        # Run the query
        query_job = client.query(query)
        results = query_job.result()

        # Extract station names
        stations = [row.station for row in results]
        
        return jsonify(stations)

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/departures/<station>')
def get_departures(station):
    """
    Returns the latest BART departure data for a specific station from BigQuery.
    """
    try:
        # Initialize BigQuery client
        client = get_bigquery_client()
        if client is None:
            return jsonify({'error': 'Failed to connect to BigQuery'}), 500

        # Construct the query to get the latest data for the specified station
        query = """
            SELECT *
            FROM `bart_data.etd_data`
            WHERE station = @station
            AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 10 MINUTE)
            ORDER BY timestamp DESC
        """

        # Set up query parameters
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("station", "STRING", station),
            ]
        )

        # Run the query
        query_job = client.query(query, job_config=job_config)
        results = query_job.result()

        # Convert results to list of dictionaries
        departures = []
        for row in results:
            departure = dict(row.items())
            # Convert timestamp objects to strings
            for key, value in departure.items():
                if isinstance(value, datetime):
                    departure[key] = value.isoformat()
            departures.append(departure)

        return jsonify({
            'status': 'success',
            'count': len(departures),
            'data': departures
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/departures')
def get_all_departures():
    """
    Returns the latest BART departure data from BigQuery.
    """
    try:
        # Initialize BigQuery client
        client = get_bigquery_client()
        if client is None:
            return jsonify({'error': 'Failed to connect to BigQuery'}), 500

        # Construct the query to get the latest data
        query = """
            SELECT *
            FROM `bart_data.etd_data`
            WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 10 MINUTE)
            ORDER BY timestamp DESC
        """

        # Run the query
        query_job = client.query(query)
        results = query_job.result()

        # Convert results to list of dictionaries
        departures = []
        for row in results:
            departure = dict(row.items())
            # Convert timestamp objects to strings
            for key, value in departure.items():
                if isinstance(value, datetime):
                    departure[key] = value.isoformat()
            departures.append(departure)

        return jsonify({
            'status': 'success',
            'count': len(departures),
            'data': departures
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 