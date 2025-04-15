import React from 'react';
import { 
  BarChart, 
  Bar, 
  LineChart, 
  Line, 
  PieChart, 
  Pie, 
  Cell,
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  Legend
} from 'recharts';
import { Departure } from '../types/bart';

interface DepartureChartsProps {
  departures: Departure[];
}

export const DepartureCharts: React.FC<DepartureChartsProps> = ({ departures }) => {
  // Group departures by destination and count them
  const destinationData = departures.reduce((acc, departure) => {
    const destination = departure.destination;
    acc[destination] = (acc[destination] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  // Transform destination data for bar chart
  const destinationChartData = Object.entries(destinationData).map(([destination, count]) => ({
    destination,
    count,
  }));

  // Group departures by platform
  const platformData = departures.reduce((acc, departure) => {
    const platform = departure.platform;
    acc[platform] = (acc[platform] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  // Transform platform data for pie chart
  const platformChartData = Object.entries(platformData).map(([platform, count]) => ({
    name: `Platform ${platform}`,
    value: count,
  }));

  // Group departures by direction and platform
  const directionPlatformData = departures.reduce((acc, departure) => {
    const platform = departure.platform;
    const direction = departure.direction;
    
    if (!acc[platform]) {
      acc[platform] = { north: 0, south: 0 };
    }
    
    if (direction.toLowerCase().includes('north')) {
      acc[platform].north += 1;
    } else if (direction.toLowerCase().includes('south')) {
      acc[platform].south += 1;
    }
    
    return acc;
  }, {} as Record<string, { north: number; south: number }>);

  // Transform direction-platform data for stacked bar chart
  const directionPlatformChartData = Object.entries(directionPlatformData).map(([platform, data]) => ({
    platform: `Platform ${platform}`,
    north: data.north,
    south: data.south,
  }));

  // Create time-based data for line chart (departures over time)
  const timeData = departures
    .sort((a, b) => a.minutes - b.minutes)
    .map(departure => ({
      time: `${departure.minutes} min`,
      count: 1,
    }))
    .reduce((acc, item) => {
      const existing = acc.find(i => i.time === item.time);
      if (existing) {
        existing.count += 1;
      } else {
        acc.push(item);
      }
      return acc;
    }, [] as { time: string; count: number }[]);

  // Colors for charts
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d'];

  return (
    <div className="space-y-8">
      {/* Destination Bar Chart */}
      <div className="h-64 w-full">
        <h2 className="text-lg font-semibold mb-2">Departures by Destination</h2>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={destinationChartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
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

      {/* Platform Distribution Pie Chart */}
      <div className="h-64 w-full">
        <h2 className="text-lg font-semibold mb-2">Departures by Platform</h2>
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={platformChartData}
              cx="50%"
              cy="50%"
              labelLine={false}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
              label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
            >
              {platformChartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Direction by Platform Stacked Bar Chart */}
      <div className="h-64 w-full">
        <h2 className="text-lg font-semibold mb-2">Direction Distribution by Platform</h2>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={directionPlatformChartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="platform" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="north" stackId="a" fill="#8884d8" name="Northbound" />
            <Bar dataKey="south" stackId="a" fill="#82ca9d" name="Southbound" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Departure Time Line Chart */}
      <div className="h-64 w-full">
        <h2 className="text-lg font-semibold mb-2">Departures Over Time</h2>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={timeData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="count" stroke="#8884d8" name="Departures" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}; 