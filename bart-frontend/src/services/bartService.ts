import { Departure } from '../types/bart';

const API_BASE_URL = 'http://localhost:5000';

export const getStations = async (): Promise<string[]> => {
  const response = await fetch(`${API_BASE_URL}/api/stations`);
  if (!response.ok) {
    throw new Error('Failed to fetch stations');
  }
  return response.json();
};

export const getDepartures = async (station: string): Promise<Departure[]> => {
  const response = await fetch(`${API_BASE_URL}/api/departures/${station}`);
  if (!response.ok) {
    throw new Error('Failed to fetch departures');
  }
  const result = await response.json();
  return result.data;
}; 