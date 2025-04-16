#!/usr/bin/env python3
"""
BART ETL Runner Script
This script starts the BART ETL scheduler as a background process.
It can be scheduled to run on system startup.
"""

import os
import sys
import subprocess
import logging
import time
from datetime import datetime

# Configure logging
log_dir = 'data/logs'
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f'bart_etl_runner_{datetime.now().strftime("%Y%m%d")}.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def is_scheduler_running():
    """Check if the ETL scheduler is already running"""
    try:
        # Check for the process
        result = subprocess.run(
            ['pgrep', '-f', 'python.*etl/scheduler.py'],
            capture_output=True,
            text=True
        )
        return bool(result.stdout.strip())
    except Exception as e:
        logger.error(f"Error checking if scheduler is running: {str(e)}")
        return False

def start_scheduler():
    """Start the ETL scheduler as a background process"""
    try:
        # Get the absolute path to the project directory
        project_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Create a log file for the scheduler
        scheduler_log = os.path.join(log_dir, f'scheduler_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        
        # Activate conda environment and run the scheduler
        cmd = [
            'conda', 'run', '-n', 'bart-env', 
            'python', os.path.join(project_dir, 'etl', 'scheduler.py')
        ]
        
        # Start the process in the background
        with open(scheduler_log, 'w') as f:
            process = subprocess.Popen(
                cmd,
                stdout=f,
                stderr=subprocess.STDOUT,
                cwd=project_dir,
                start_new_session=True  # This makes it run in the background
            )
        
        logger.info(f"Started ETL scheduler with PID {process.pid}")
        logger.info(f"Scheduler output will be logged to {scheduler_log}")
        
        return process.pid
    except Exception as e:
        logger.error(f"Error starting scheduler: {str(e)}")
        return None

def main():
    """Main function to run the ETL scheduler"""
    logger.info("Starting BART ETL runner")
    
    # Check if scheduler is already running
    if is_scheduler_running():
        logger.info("ETL scheduler is already running. Exiting.")
        return
    
    # Start the scheduler
    pid = start_scheduler()
    if pid:
        logger.info(f"ETL scheduler started successfully with PID {pid}")
    else:
        logger.error("Failed to start ETL scheduler")
        sys.exit(1)

if __name__ == "__main__":
    main() 