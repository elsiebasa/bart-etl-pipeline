#!/bin/bash
# Script to deploy BART ETL to Google Cloud Functions

# Exit on error
set -e

# Configuration
PROJECT_ID="your-project-id"  # Replace with your GCP project ID
REGION="us-central1"          # Replace with your preferred region
FUNCTION_NAME="bart-etl"
ENTRY_POINT="run_bart_etl"
RUNTIME="python39"
MEMORY="256MB"
TIMEOUT="540s"  # 9 minutes (maximum for free tier)
SCHEDULE="*/15 * * * *"  # Run every 15 minutes

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "gcloud CLI is not installed. Please install it first."
    exit 1
fi

# Check if user is logged in
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "@"; then
    echo "You are not logged in to gcloud. Please run 'gcloud auth login' first."
    exit 1
fi

# Set the project
echo "Setting project to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

# Create a temporary directory for deployment
echo "Creating temporary deployment directory..."
TEMP_DIR=$(mktemp -d)
cp cloud_function_etl.py $TEMP_DIR/
cp requirements.txt $TEMP_DIR/
cp -r etl $TEMP_DIR/

# Deploy the function
echo "Deploying Cloud Function..."
gcloud functions deploy $FUNCTION_NAME \
    --gen2 \
    --runtime=$RUNTIME \
    --region=$REGION \
    --source=$TEMP_DIR \
    --entry-point=$ENTRY_POINT \
    --trigger-http \
    --memory=$MEMORY \
    --timeout=$TIMEOUT \
    --min-instances=0 \
    --max-instances=1

# Create a Cloud Scheduler job to trigger the function
echo "Creating Cloud Scheduler job..."
gcloud scheduler jobs create http $FUNCTION_NAME-trigger \
    --schedule="$SCHEDULE" \
    --uri=$(gcloud functions describe $FUNCTION_NAME --gen2 --region=$REGION --format="value(serviceConfig.uri)") \
    --http-method=GET \
    --attempt-deadline=10m \
    --time-zone="America/Los_Angeles"

echo "Deployment complete!"
echo "Your BART ETL function is now running on Google Cloud Functions."
echo "It will be triggered every 15 minutes by Cloud Scheduler."
echo "You can monitor it in the Google Cloud Console." 