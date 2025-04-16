import sqlite3
from datetime import datetime, timedelta
import json

class BARTDataStore:
    def __init__(self, db_path='bart_history.db'):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Create tables
        c.execute('''
            CREATE TABLE IF NOT EXISTS departures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                station TEXT,
                destination TEXT,
                platform TEXT,
                minutes INTEGER,
                direction TEXT,
                color TEXT,
                length INTEGER,
                bike_flag INTEGER,
                delay INTEGER,
                timestamp DATETIME,
                date DATE
            )
        ''')
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS daily_stats (
                date DATE PRIMARY KEY,
                total_departures INTEGER,
                total_delays INTEGER,
                avg_delay_minutes REAL
            )
        ''')
        
        conn.commit()
        conn.close()

    def store_departure(self, departure_data):
        """Store a single departure record"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        now = datetime.now()
        date = now.date()
        
        c.execute('''
            INSERT INTO departures (
                station, destination, platform, minutes, direction,
                color, length, bike_flag, delay, timestamp, date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            departure_data['station'],
            departure_data['destination'],
            departure_data['platform'],
            departure_data['minutes'],
            departure_data['direction'],
            departure_data['color'],
            departure_data['length'],
            departure_data['bike_flag'],
            departure_data['delay'],
            now,
            date
        ))
        
        conn.commit()
        conn.close()

    def get_daily_stats(self, days=10):
        """Get statistics for the last N days"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        c.execute('''
            SELECT date, COUNT(*) as total_departures,
                   SUM(CASE WHEN delay > 0 THEN 1 ELSE 0 END) as total_delays,
                   AVG(CASE WHEN delay > 0 THEN delay ELSE NULL END) as avg_delay
            FROM departures
            WHERE date >= ? AND date <= ?
            GROUP BY date
            ORDER BY date DESC
        ''', (start_date, end_date))
        
        stats = c.fetchall()
        conn.close()
        
        return [{
            'date': row[0],
            'total_departures': row[1],
            'total_delays': row[2],
            'avg_delay_minutes': row[3]
        } for row in stats]

    def get_station_stats(self, station, days=10):
        """Get statistics for a specific station"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        c.execute('''
            SELECT 
                destination,
                COUNT(*) as total_departures,
                AVG(CASE WHEN delay > 0 THEN delay ELSE NULL END) as avg_delay,
                COUNT(CASE WHEN delay > 0 THEN 1 END) as delay_count
            FROM departures
            WHERE station = ? AND date >= ? AND date <= ?
            GROUP BY destination
            ORDER BY total_departures DESC
        ''', (station, start_date, end_date))
        
        stats = c.fetchall()
        conn.close()
        
        return [{
            'destination': row[0],
            'total_departures': row[1],
            'avg_delay_minutes': row[2],
            'delay_count': row[3]
        } for row in stats]

    def cleanup_old_data(self, days_to_keep=30):
        """Remove data older than specified days"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        cutoff_date = datetime.now().date() - timedelta(days=days_to_keep)
        
        c.execute('DELETE FROM departures WHERE date < ?', (cutoff_date,))
        c.execute('DELETE FROM daily_stats WHERE date < ?', (cutoff_date,))
        
        conn.commit()
        conn.close() 