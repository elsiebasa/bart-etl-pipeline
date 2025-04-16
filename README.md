# BART ETL Pipeline

A data pipeline that collects real-time BART transit data and stores it in BigQuery for analysis.

## Overview

This project fetches data from the BART API, processes it, and loads it into BigQuery tables. The pipeline runs on a schedule using GitHub Actions, allowing for continuous data collection without keeping your computer on.

## Features

- Fetches real-time BART station and departure data
- Processes and cleans the data
- Stores data in BigQuery for analysis
- Runs automatically on a schedule using GitHub Actions
- Completely free solution with no credit card required

## Data Structure

The pipeline collects and stores three types of data:

1. **Stations**: Information about BART stations
2. **Departures**: Real-time departure information
3. **Metrics**: Calculated metrics about BART operations

## Setup

See the [CLOUD_DEPLOYMENT.md](CLOUD_DEPLOYMENT.md) file for detailed setup instructions.

## License

MIT 