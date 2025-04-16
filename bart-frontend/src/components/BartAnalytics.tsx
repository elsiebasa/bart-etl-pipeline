import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  CircularProgress,
  Box
} from '@mui/material';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';

interface DailyStats {
  date: string;
  station: string;
  total_departures: number;
  total_delays: number;
  avg_delay_minutes: number;
}

interface DelayPattern {
  hour: number;
  station: string;
  avg_delay: number;
  total_trains: number;
}

interface StationStats {
  destination: string;
  total_departures: number;
  avg_delay_minutes: number;
  delay_count: number;
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

const BartAnalytics: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [selectedStation, setSelectedStation] = useState('12th St. Oakland City Center');
  const [days, setDays] = useState(7);
  const [dailyStats, setDailyStats] = useState<DailyStats[]>([]);
  const [delayPatterns, setDelayPatterns] = useState<DelayPattern[]>([]);
  const [stationStats, setStationStats] = useState<StationStats[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        // Fetch daily stats
        const dailyResponse = await fetch(`/api/analytics/daily?days=${days}`);
        const dailyData = await dailyResponse.json();
        setDailyStats(dailyData);

        // Fetch delay patterns
        const delayResponse = await fetch(`/api/analytics/delays?days=${days}`);
        const delayData = await delayResponse.json();
        setDelayPatterns(delayData);

        // Fetch station stats
        const stationResponse = await fetch(`/api/analytics/station?station=${encodeURIComponent(selectedStation)}&days=${days}`);
        const stationData = await stationResponse.json();
        setStationStats(stationData);
      } catch (error) {
        console.error('Error fetching analytics:', error);
      }
      setLoading(false);
    };

    fetchData();
  }, [selectedStation, days]);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Grid container spacing={3}>
        {/* Controls */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2, display: 'flex', gap: 2 }}>
            <FormControl sx={{ minWidth: 200 }}>
              <InputLabel>Station</InputLabel>
              <Select
                value={selectedStation}
                label="Station"
                onChange={(e) => setSelectedStation(e.target.value)}
              >
                <MenuItem value="12th St. Oakland City Center">12th St. Oakland City Center</MenuItem>
                <MenuItem value="16th St. Mission">16th St. Mission</MenuItem>
                <MenuItem value="19th St. Oakland">19th St. Oakland</MenuItem>
                <MenuItem value="24th St. Mission">24th St. Mission</MenuItem>
              </Select>
            </FormControl>
            <FormControl sx={{ minWidth: 120 }}>
              <InputLabel>Days</InputLabel>
              <Select
                value={days}
                label="Days"
                onChange={(e) => setDays(Number(e.target.value))}
              >
                <MenuItem value={7}>Last 7 days</MenuItem>
                <MenuItem value={14}>Last 14 days</MenuItem>
                <MenuItem value={30}>Last 30 days</MenuItem>
              </Select>
            </FormControl>
          </Paper>
        </Grid>

        {/* Daily Departures Chart */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Daily Departures
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={dailyStats}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="total_departures" stroke="#8884d8" />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Delay Analysis */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Daily Delays
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={dailyStats}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="total_delays" fill="#82ca9d" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Average Delay Duration
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={dailyStats}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="avg_delay_minutes" stroke="#ff7300" />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Station Analysis */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Departures by Destination
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={stationStats}
                  dataKey="total_departures"
                  nameKey="destination"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  label
                >
                  {stationStats.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Average Delay by Destination
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={stationStats}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="destination" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="avg_delay_minutes" fill="#8884d8" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default BartAnalytics; 