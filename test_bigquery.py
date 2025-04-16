import sqlite3
from datetime import datetime, timezone
import os
import json

def setup_sqlite_database():
    """Create SQLite database and tables"""
    try:
        # Create database directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        
        # Connect to SQLite database
        conn = sqlite3.connect('data/bart.db')
        cursor = conn.cursor()
        
        # Create departures table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS departures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP NOT NULL,
            station TEXT NOT NULL,
            destination TEXT NOT NULL,
            minutes INTEGER NOT NULL,
            platform TEXT,
            direction TEXT,
            delay INTEGER,
            length INTEGER
        )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON departures(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_station ON departures(station)')
        
        conn.commit()
        return conn
    except Exception as e:
        print(f"Error setting up database: {str(e)}")
        raise e

def test_database():
    """Test SQLite database operations"""
    try:
        # Setup database
        print("Setting up SQLite database...")
        conn = setup_sqlite_database()
        cursor = conn.cursor()
        
        # Insert test data
        print("\nInserting test data...")
        current_time = datetime.now(timezone.utc)
        cursor.execute('''
        INSERT INTO departures (timestamp, station, destination, minutes, platform, direction, delay, length)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (current_time, "Test Station", "Test Destination", 5, "1", "North", 0, 8))
        
        conn.commit()
        print("Test data inserted successfully")
        
        # Query test data
        print("\nQuerying recent departures...")
        cursor.execute('''
        SELECT timestamp, station, destination, minutes, delay
        FROM departures
        ORDER BY timestamp DESC
        LIMIT 5
        ''')
        
        rows = cursor.fetchall()
        print("\nRecent departures:")
        for row in rows:
            print(f"Station: {row[1]}, Destination: {row[2]}, "
                  f"Minutes: {row[3]}, Delay: {row[4]}")
        
        # Show some statistics
        print("\nCalculating statistics...")
        cursor.execute('''
        SELECT 
            COUNT(*) as total_departures,
            AVG(CASE WHEN delay > 0 THEN delay END) as avg_delay,
            COUNT(CASE WHEN delay > 0 THEN 1 END) as delayed_trains
        FROM departures
        WHERE timestamp >= datetime('now', '-7 days')
        ''')
        
        stats = cursor.fetchone()
        print(f"Last 7 days statistics:")
        print(f"Total departures: {stats[0]}")
        print(f"Average delay: {stats[1] if stats[1] else 0:.2f} minutes")
        print(f"Delayed trains: {stats[2]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error in database operations: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    test_database() 