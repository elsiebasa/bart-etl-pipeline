import React, { useEffect, useState } from 'react';
import { Departure } from '../types/bart';
import { getStations, getDepartures } from '../services/bartService';
import { DepartureCharts } from './DepartureCharts';

export const DepartureBoard: React.FC = () => {
  const [stations, setStations] = useState<string[]>([]);
  const [selectedStation, setSelectedStation] = useState<string>('');
  const [departures, setDepartures] = useState<Departure[]>([]);
  const [error, setError] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  useEffect(() => {
    const fetchStations = async () => {
      try {
        const stationList = await getStations();
        setStations(stationList);
        if (stationList.length > 0) {
          setSelectedStation(stationList[0]);
        }
      } catch (err) {
        setError('Failed to load stations');
      }
    };
    fetchStations();
  }, []);

  useEffect(() => {
    const fetchDepartures = async () => {
      if (!selectedStation) return;
      try {
        setIsLoading(true);
        const departureList = await getDepartures(selectedStation);
        setDepartures(departureList);
        setLastUpdated(new Date());
        setError('');
      } catch (err) {
        setError('Failed to load departures');
      } finally {
        setIsLoading(false);
      }
    };

    // Initial fetch
    fetchDepartures();

    // Set up polling every 2 minutes (120000 ms)
    const interval = setInterval(fetchDepartures, 120000);
    return () => clearInterval(interval);
  }, [selectedStation]);

  return (
    <div className="p-4">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">BART Departures</h1>
        {lastUpdated && (
          <span className="text-sm text-gray-500">
            Last updated: {lastUpdated.toLocaleTimeString()}
          </span>
        )}
      </div>
      
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700">Select Station:</label>
        <select
          value={selectedStation}
          onChange={(e) => setSelectedStation(e.target.value)}
          className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
          disabled={isLoading}
        >
          {stations.map((station) => (
            <option key={station} value={station}>
              {station}
            </option>
          ))}
        </select>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4">
          {error}
        </div>
      )}

      {isLoading && (
        <div className="text-center py-4">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-gray-300 border-t-indigo-600"></div>
          <p className="mt-2 text-sm text-gray-500">Updating departure information...</p>
        </div>
      )}

      <DepartureCharts departures={departures} />

      <div className="overflow-x-auto mt-4">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Destination</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Direction</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Minutes</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Platform</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Bike Flag</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Delay</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {departures.map((departure, index) => (
              <tr key={index}>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{departure.destination}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{departure.direction}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{departure.minutes}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{departure.platform}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{departure.bike_flag ? 'Yes' : 'No'}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{departure.delay} min</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}; 