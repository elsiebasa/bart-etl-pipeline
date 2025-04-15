from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
from bart_etd import fetch_bart_etd, get_bigquery_client, upload_to_bigquery

def job():
    """
    Main job function that fetches BART ETD data and uploads it to BigQuery.
    """
    print(f"\n[{datetime.now()}] Starting BART ETD data collection...")
    
    # Initialize BigQuery client
    bq_client = get_bigquery_client()
    if bq_client is None:
        print("Failed to initialize BigQuery client. Skipping this run.")
        return
    
    # Fetch ETD data
    etd_df = fetch_bart_etd()
    
    if etd_df is not None:
        print(f"Fetched {len(etd_df)} records")
        
        # Upload to BigQuery
        dataset_id = "bart_data"
        table_id = "etd_data"
        
        if upload_to_bigquery(bq_client, etd_df, dataset_id, table_id):
            print("Successfully uploaded data to BigQuery")
        else:
            print("Failed to upload data to BigQuery")
    else:
        print("Failed to fetch BART ETD data")

def main():
    """
    Main function that sets up and runs the scheduler.
    """
    print("Starting BART ETD data collection scheduler...")
    print("The script will run every 5 minutes")
    
    # Create the scheduler
    scheduler = BackgroundScheduler()
    
    # Add the job to the scheduler
    scheduler.add_job(
        func=job,
        trigger=IntervalTrigger(minutes=5),
        id='bart_etd_job',
        name='BART ETD Data Collection',
        replace_existing=True
    )
    
    # Start the scheduler
    scheduler.start()
    
    try:
        # Run the job immediately
        job()
        
        # Keep the script running
        while True:
            time.sleep(1)
            
    except (KeyboardInterrupt, SystemExit):
        print("\nScheduler stopped by user")
        scheduler.shutdown()
    except Exception as e:
        print(f"Error in scheduler: {e}")
        scheduler.shutdown()

if __name__ == "__main__":
    main() 