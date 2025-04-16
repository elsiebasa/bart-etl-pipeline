# Deploying BART ETL to Google Cloud Functions

This guide will help you deploy your BART ETL pipeline to Google Cloud Functions, allowing it to run on a schedule without keeping your computer on.

## Prerequisites

1. A Google Cloud Platform (GCP) account
2. Google Cloud SDK (gcloud) installed on your computer
3. A GCP project created
4. BigQuery API enabled in your project
5. Cloud Functions API enabled in your project
6. Cloud Scheduler API enabled in your project

## Setup Steps

### 1. Install Google Cloud SDK

If you haven't already installed the Google Cloud SDK, follow these steps:

- Visit [Google Cloud SDK installation page](https://cloud.google.com/sdk/docs/install)
- Download and install the SDK for your operating system
- Run `gcloud init` to initialize the SDK

### 2. Create a GCP Project (if you don't have one)

```bash
gcloud projects create [PROJECT_ID] --name="BART ETL Project"
gcloud config set project [PROJECT_ID]
```

Replace `[PROJECT_ID]` with your desired project ID.

### 3. Enable Required APIs

```bash
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable cloudscheduler.googleapis.com
gcloud services enable bigquery.googleapis.com
```

### 4. Set Up BigQuery

Make sure your BigQuery dataset and tables are created:

```bash
# Create dataset if it doesn't exist
bq mk --dataset [PROJECT_ID]:bart_data

# Create tables (if they don't exist)
bq mk --table [PROJECT_ID]:bart_data.stations station_id:STRING,name:STRING,abbr:STRING,latitude:FLOAT,longitude:FLOAT
bq mk --table [PROJECT_ID]:bart_data.departures station_id:STRING,destination:STRING,direction:STRING,estimated_minutes:INTEGER,platform:STRING,bike_flag:BOOLEAN,delay:INTEGER,color:STRING,length:INTEGER,timestamp:TIMESTAMP
bq mk --table [PROJECT_ID]:bart_data.metrics date:DATE,total_trains:INTEGER,avg_delay:FLOAT,delayed_trains:INTEGER
```

### 5. Update Deployment Script

Edit the `deploy_to_gcp.sh` script and replace `your-project-id` with your actual GCP project ID.

### 6. Deploy to Cloud Functions

Make the deployment script executable and run it:

```bash
chmod +x deploy_to_gcp.sh
./deploy_to_gcp.sh
```

## Free Tier Considerations

Google Cloud Functions offers a generous free tier:

- 2 million invocations per month
- 400,000 GB-seconds of compute time
- 200,000 CPU-seconds of compute time
- 5GB of outbound data transfer

With the configuration in the deployment script:
- The function runs every 15 minutes (96 times per day, ~2,880 times per month)
- Each function uses 256MB of memory
- The maximum execution time is 9 minutes (540 seconds)

This configuration should stay within the free tier limits for most use cases.

## Monitoring

You can monitor your Cloud Function in the Google Cloud Console:

1. Go to [Cloud Functions](https://console.cloud.google.com/functions)
2. Select your function (`bart-etl`)
3. View logs, metrics, and execution history

## Troubleshooting

If you encounter issues:

1. Check the Cloud Function logs in the Google Cloud Console
2. Verify that your BigQuery credentials are correctly set up
3. Ensure your BART API key is valid
4. Check that the Cloud Scheduler job is running correctly

## Cost Management

To ensure you stay within the free tier:

1. Monitor your usage in the Google Cloud Console
2. Adjust the schedule if needed (e.g., run every 30 minutes instead of 15)
3. Set up budget alerts to be notified if you approach the free tier limits 