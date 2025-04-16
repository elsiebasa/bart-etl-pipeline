import { Departure, Station } from '../types/bart';

const API_BASE_URL = 'http://localhost:5000';

export const getStations = async (): Promise<Station[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/stations`);
    if (!response.ok) {
      throw new Error('Failed to fetch stations');
    }
    const data = await response.json();
    return data || [];
  } catch (error) {
    console.error('Error fetching stations:', error);
    throw error;
  }
};

export const getDepartures = async (stationAbbr: string): Promise<Departure[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/departures/${stationAbbr}`);
    if (!response.ok) {
      throw new Error('Failed to fetch departures');
    }
    const data = await response.json();
    return data || [];
  } catch (error) {
    console.error('Error fetching departures:', error);
    throw error;
  }
};

export const getDailyAnalytics = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/analytics/daily`);
    if (!response.ok) {
      throw new Error('Failed to fetch daily analytics');
    }
    const data = await response.json();
    return data || [];
  } catch (error) {
    console.error('Error fetching daily analytics:', error);
    throw error;
  }
};

export const getStationAnalytics = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/analytics/stations`);
    if (!response.ok) {
      throw new Error('Failed to fetch station analytics');
    }
    const data = await response.json();
    return data || [];
  } catch (error) {
    console.error('Error fetching station analytics:', error);
    throw error;
  }
}; 