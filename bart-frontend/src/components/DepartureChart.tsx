import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Departure } from '../types/bart';

interface DepartureChartProps {
  departures: Departure[];
}

export const DepartureChart: React.FC<DepartureChartProps> = ({ departures }) => {
  // Group departures by destination and count them
  const departureData = departures.reduce((acc, departure) => {
    const destination = departure.destination;
    acc[destination] = (acc[destination] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  // Transform data for Recharts
  const chartData = Object.entries(departureData).map(([destination, count]) => ({
    destination,
    count,
  }));

  return (
    <div className="h-64 w-full mt-4">
      <h2 className="text-lg font-semibold mb-2">Departures by Destination</h2>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="destination" 
            angle={-45}
            textAnchor="end"
            height={60}
            interval={0}
          />
          <YAxis />
          <Tooltip />
          <Bar dataKey="count" fill="#8884d8" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}; 