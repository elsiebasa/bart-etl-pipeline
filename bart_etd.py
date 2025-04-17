import requests
import pandas as pd
from datetime import datetime, timezone
from google.cloud import bigquery
from google.oauth2 import service_account

def get_bigquery_client():
    """
    Authenticates and returns a BigQuery client using service account credentials.
    """
    try:
        # Path to your service account key JSON file
        credentials = service_account.Credentials.from_service_account_file(
            'service-account-key.json',
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )
        
        # Create BigQuery client
        client = bigquery.Client(credentials=credentials, project=credentials.project_id)
        return client
    except Exception as e:
        print(f"Error connecting to BigQuery: {e}")
        return None

def ensure_table_exists(client, dataset_id, table_id, df):
    """
    Creates a BigQuery table if it doesn't exist, using the DataFrame's schema.
    """
    # Construct full table reference
    table_ref = f"{client.project}.{dataset_id}.{table_id}"
    
    # Check if table exists
    try:
        client.get_table(table_ref)
        print(f"Table {table_ref} already exists.")
        return True
    except Exception:
        print(f"Table {table_ref} does not exist. Creating...")
        
        # Create schema from DataFrame
        schema = []
        for column in df.columns:
            # Map pandas dtypes to BigQuery types
            dtype = str(df[column].dtype)
            if 'int' in dtype:
                field_type = 'INTEGER'
            elif 'float' in dtype:
                field_type = 'FLOAT'
            elif 'datetime' in dtype:
                field_type = 'TIMESTAMP'
            else:
                field_type = 'STRING'
            
            schema.append(bigquery.SchemaField(column, field_type))
        
        # Create table
        table = bigquery.Table(table_ref, schema=schema)
        table = client.create_table(table)
        print(f"Created table {table_ref}")
        return True

def upload_to_bigquery(client, df, dataset_id, table_id):
    """
    Uploads DataFrame to BigQuery table.
    """
    try:
        # Ensure table exists
        if not ensure_table_exists(client, dataset_id, table_id, df):
            return False
        
        # Construct full table reference
        table_ref = f"{client.project}.{dataset_id}.{table_id}"
        
        # Upload DataFrame to BigQuery
        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND
        )
        
        job = client.load_table_from_dataframe(
            df, table_ref, job_config=job_config
        )
        job.result()  # Wait for the job to complete
        
        print(f"Loaded {len(df)} rows into {table_ref}")
        return True
        
    except Exception as e:
        print(f"Error uploading to BigQuery: {e}")
        return False

def fetch_bart_etd():
    """
    Fetches real-time ETD data from BART API and returns it as a Pandas DataFrame.
    """
    # BART API endpoint
    url = "http://api.bart.gov/api/etd.aspx"
    
    # API parameters
    params = {
        "cmd": "etd",
        "orig": "ALL",
        "key": "MW9S-E7SL-26DU-VV8V",
        "json": "y"
    }
    
    try:
        # Make the API request
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Parse the JSON response
        data = response.json()
        
        # Get current UTC time
        current_utc = datetime.now(timezone.utc)
        
        # Extract ETD data
        etd_data = []
        
        # Check if the response contains ETD data
        if 'root' in data and 'station' in data['root']:
            for station in data['root']['station']:
                station_name = station['name']
                
                # Process each destination's ETD information
                for etd in station['etd']:
                    destination = etd['destination']
                    
                    # Process each estimate
                    for estimate in etd['estimate']:
                        for direction in estimate['direction']:
                            for train in direction['train']:
                                etd_data.append({
                                    'station': station_name,
                                    'destination': destination,
                                    'direction': direction['direction'],
                                    'minutes': train['minutes'],
                                    'platform': train['platform'],
                                    'bike_flag': train['bikeflag'],
                                    'delay': train['delay'],
                                    'timestamp': current_utc.strftime('%Y-%m-%d %H:%M:%S'),
                                    'retrieved_at': current_utc.strftime('%Y-%m-%d %H:%M:%S UTC')
                                })
        
        # Convert to DataFrame
        df = pd.DataFrame(etd_data)
        return df
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from BART API: {e}")
        return None

if __name__ == "__main__":
    # Initialize BigQuery client
    bq_client = get_bigquery_client()
    if bq_client is None:
        print("Failed to initialize BigQuery client. Exiting...")
        exit(1)
    
    # Fetch ETD data
    etd_df = fetch_bart_etd()
    
    if etd_df is not None:
        print("\nBART ETD Data:")
        print(etd_df)
        
        # Save to CSV file
        etd_df.to_csv('bart_etd_data.csv', index=False)
        print("\nData saved to 'bart_etd_data.csv'")
        
        # Upload to BigQuery
        dataset_id = "bart_data"
        table_id = "etd_data"
        
        if upload_to_bigquery(bq_client, etd_df, dataset_id, table_id):
            print("Successfully uploaded data to BigQuery")
        else:
            print("Failed to upload data to BigQuery") 