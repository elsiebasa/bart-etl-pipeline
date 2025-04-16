import streamlit as st
import pandas as pd
from google.cloud import bigquery
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# Initialize BigQuery client
client = bigquery.Client()

def load_daily_stats(days=7):
    """Load daily statistics from BigQuery"""
    query = f"""
    SELECT
        DATE(timestamp) as date,
        station,
        COUNT(*) as total_departures,
        SUM(CASE WHEN delay > 0 THEN 1 ELSE 0 END) as total_delays,
        AVG(CASE WHEN delay > 0 THEN delay ELSE NULL END) as avg_delay_minutes
    FROM `bart_data.departures`
    WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
    GROUP BY date, station
    ORDER BY date DESC, station
    """
    return client.query(query).to_dataframe()

def load_delay_patterns(days=7):
    """Load delay patterns from BigQuery"""
    query = f"""
    SELECT
        DATE(timestamp) as date,
        HOUR(timestamp) as hour,
        station,
        AVG(delay) as avg_delay,
        COUNT(*) as total_trains
    FROM `bart_data.departures`
    WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
    AND delay > 0
    GROUP BY date, hour, station
    ORDER BY date DESC, hour
    """
    return client.query(query).to_dataframe()

def load_station_stats(station, days=7):
    """Load statistics for a specific station"""
    query = f"""
    SELECT
        destination,
        COUNT(*) as total_departures,
        AVG(CASE WHEN delay > 0 THEN delay ELSE NULL END) as avg_delay_minutes,
        COUNT(CASE WHEN delay > 0 THEN 1 END) as delay_count
    FROM `bart_data.departures`
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
    return client.query(query, job_config=job_config).to_dataframe()

# Streamlit app
st.title("BART Transit Analytics Dashboard")

# Sidebar controls
st.sidebar.header("Controls")
days = st.sidebar.slider("Days of data to show", 1, 30, 7)
station = st.sidebar.selectbox(
    "Select Station",
    ["12th St. Oakland City Center", "16th St. Mission", "19th St. Oakland", "24th St. Mission"]
)

# Load data
daily_stats = load_daily_stats(days)
delay_patterns = load_delay_patterns(days)
station_stats = load_station_stats(station, days)

# Daily Departures Chart
st.header("Daily Departures")
fig_departures = px.line(
    daily_stats,
    x="date",
    y="total_departures",
    color="station",
    title="Daily Departures by Station"
)
st.plotly_chart(fig_departures)

# Delay Analysis
st.header("Delay Analysis")
col1, col2 = st.columns(2)

with col1:
    fig_delays = px.bar(
        daily_stats,
        x="date",
        y="total_delays",
        color="station",
        title="Daily Delays by Station"
    )
    st.plotly_chart(fig_delays)

with col2:
    fig_avg_delay = px.line(
        daily_stats,
        x="date",
        y="avg_delay_minutes",
        color="station",
        title="Average Delay Duration"
    )
    st.plotly_chart(fig_avg_delay)

# Delay Patterns by Hour
st.header("Delay Patterns by Hour")
fig_hourly = px.heatmap(
    delay_patterns,
    x="hour",
    y="station",
    z="avg_delay",
    title="Average Delays by Hour and Station"
)
st.plotly_chart(fig_hourly)

# Station-specific Analysis
st.header(f"Analysis for {station}")
col3, col4 = st.columns(2)

with col3:
    fig_destinations = px.pie(
        station_stats,
        values="total_departures",
        names="destination",
        title="Departures by Destination"
    )
    st.plotly_chart(fig_destinations)

with col4:
    fig_delays_by_dest = px.bar(
        station_stats,
        x="destination",
        y="avg_delay_minutes",
        title="Average Delay by Destination"
    )
    st.plotly_chart(fig_delays_by_dest)

# Raw Data Tables
st.header("Raw Data")
tab1, tab2, tab3 = st.tabs(["Daily Stats", "Delay Patterns", "Station Stats"])

with tab1:
    st.dataframe(daily_stats)

with tab2:
    st.dataframe(delay_patterns)

with tab3:
    st.dataframe(station_stats) 