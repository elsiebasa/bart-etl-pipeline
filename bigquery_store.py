from google.cloud import bigquery
from datetime import datetime
import json

class BARTBigQueryStore:
    def __init__(self, project_id, dataset_id='bart_data'):
        self.client = bigquery.Client(project=project_id)
        self.dataset_id = dataset_id
        self.init_tables()

    def init_tables(self):
        """Initialize BigQuery tables if they don't exist"""
        dataset_ref = self.client.dataset(self.dataset_id)
        
        # Create departures table schema
        departures_schema = [
            bigquery.SchemaField("timestamp", "TIMESTAMP"),
            bigquery.SchemaField("station", "STRING"),
            bigquery.SchemaField("destination", "STRING"),
            bigquery.SchemaField("platform", "STRING"),
            bigquery.SchemaField("minutes", "INTEGER"),
            bigquery.SchemaField("direction", "STRING"),
            bigquery.SchemaField("color", "STRING"),
            bigquery.SchemaField("length", "INTEGER"),
            bigquery.SchemaField("bike_flag", "BOOLEAN"),
            bigquery.SchemaField("delay", "INTEGER")
        ]
        
        # Create daily_stats table schema
        daily_stats_schema = [
            bigquery.SchemaField("date", "DATE"),
            bigquery.SchemaField("station", "STRING"),
            bigquery.SchemaField("total_departures", "INTEGER"),
            bigquery.SchemaField("total_delays", "INTEGER"),
            bigquery.SchemaField("avg_delay_minutes", "FLOAT")
        ]

        # Create tables if they don't exist
        departures_table = bigquery.Table(f"{self.dataset_id}.departures", schema=departures_schema)
        stats_table = bigquery.Table(f"{self.dataset_id}.daily_stats", schema=daily_stats_schema)
        
        try:
            self.client.create_table(departures_table, exists_ok=True)
            self.client.create_table(stats_table, exists_ok=True)
        except Exception as e:
            print(f"Error creating tables: {e}")

    def store_departure(self, departure_data):
        """Store a single departure record in BigQuery"""
        table_id = f"{self.dataset_id}.departures"
        table = self.client.get_table(table_id)
        
        # Prepare the row data
        row = {
            "timestamp": datetime.now(),
            "station": departure_data["station"],
            "destination": departure_data["destination"],
            "platform": departure_data["platform"],
            "minutes": departure_data["minutes"],
            "direction": departure_data["direction"],
            "color": departure_data["color"],
            "length": departure_data["length"],
            "bike_flag": departure_data["bike_flag"],
            "delay": departure_data["delay"]
        }
        
        # Insert the row
        errors = self.client.insert_rows_json(table, [row])
        if errors:
            print(f"Errors inserting rows: {errors}")

    def get_daily_stats(self, days=10):
        """Get statistics for the last N days using BigQuery"""
        query = f"""
        SELECT
            DATE(timestamp) as date,
            station,
            COUNT(*) as total_departures,
            SUM(CASE WHEN delay > 0 THEN 1 ELSE 0 END) as total_delays,
            AVG(CASE WHEN delay > 0 THEN delay ELSE NULL END) as avg_delay_minutes
        FROM `{self.dataset_id}.departures`
        WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
        GROUP BY date, station
        ORDER BY date DESC, station
        """
        
        query_job = self.client.query(query)
        return [dict(row.items()) for row in query_job]

    def get_station_stats(self, station, days=10):
        """Get statistics for a specific station"""
        query = f"""
        SELECT
            destination,
            COUNT(*) as total_departures,
            AVG(CASE WHEN delay > 0 THEN delay ELSE NULL END) as avg_delay_minutes,
            COUNT(CASE WHEN delay > 0 THEN 1 END) as delay_count
        FROM `{self.dataset_id}.departures`
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
        
        query_job = self.client.query(query, job_config=job_config)
        return [dict(row.items()) for row in query_job]

    def get_delay_patterns(self, days=30):
        """Analyze delay patterns over time"""
        query = f"""
        SELECT
            DATE(timestamp) as date,
            HOUR(timestamp) as hour,
            station,
            AVG(delay) as avg_delay,
            COUNT(*) as total_trains
        FROM `{self.dataset_id}.departures`
        WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
        AND delay > 0
        GROUP BY date, hour, station
        ORDER BY date DESC, hour
        """
        
        query_job = self.client.query(query)
        return [dict(row.items()) for row in query_job] 