import React, { useEffect, useState } from 'react';
import { 
  Container, 
  Typography, 
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Box,
  CircularProgress,
  Alert,
  Select,
  MenuItem,
  FormControl,
  InputLabel
} from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { getDepartures, getStations } from '../services/bartService';
import { Departure, Station } from '../types/bart';

interface DelayDataPoint {
  time: string;
  delay: number;
}

function BartAnalytics() {
  const [departures, setDepartures] = useState<Departure[]>([]);
  const [stations, setStations] = useState<Station[]>([]);
  const [selectedStation, setSelectedStation] = useState<string>('12TH');
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadStations = async () => {
      try {
        const stationData = await getStations();
        setStations(stationData);
      } catch (err) {
        console.error('Failed to load stations:', err);
      }
    };
    loadStations();
  }, []);

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const data = await getDepartures(selectedStation);
        setDepartures(data);
        setError(null);
      } catch (err) {
        setError('Failed to load departure data');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    loadData();
    // Refresh every 30 seconds
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, [selectedStation]);

  // Transform departure data for the delay chart
  const delayData: DelayDataPoint[] = departures.map((d) => ({
    time: d.timestamp && typeof d.timestamp === 'string' 
      ? new Date(d.timestamp).toLocaleTimeString() 
      : 'Unknown',
    delay: d.delay || 0
  }));

  if (loading && !departures.length) {
    return (
      <Box display="flex" justifyContent="center" my={4}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom sx={{ color: '#000000' }}>
        BART Departures Analytics
      </Typography>

      {/* Station Selector */}
      <Paper sx={{ mb: 4, p: 2, backgroundColor: '#ffffff' }}>
        <FormControl fullWidth>
          <InputLabel id="station-select-label" sx={{ color: '#000000' }}>Select Station</InputLabel>
          <Select
            labelId="station-select-label"
            value={selectedStation}
            onChange={(e) => setSelectedStation(e.target.value)}
            sx={{ color: '#000000' }}
          >
            {stations.map((station) => (
              <MenuItem key={station.abbr} value={station.abbr}>
                {station.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Paper>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {/* Recent Departures Table */}
      <Paper sx={{ mb: 4, backgroundColor: '#ffffff' }}>
        <Typography variant="h6" sx={{ p: 2, color: '#000000' }}>
          Recent Departures
        </Typography>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell sx={{ color: '#000000', fontWeight: 'bold' }}>Time</TableCell>
                <TableCell sx={{ color: '#000000', fontWeight: 'bold' }}>Destination</TableCell>
                <TableCell sx={{ color: '#000000', fontWeight: 'bold' }}>Minutes</TableCell>
                <TableCell sx={{ color: '#000000', fontWeight: 'bold' }}>Platform</TableCell>
                <TableCell sx={{ color: '#000000', fontWeight: 'bold' }}>Direction</TableCell>
                <TableCell sx={{ color: '#000000', fontWeight: 'bold' }}>Train Info</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {departures.map((departure, index) => (
                <TableRow key={index}>
                  <TableCell sx={{ color: '#000000' }}>
                    {departure.timestamp && typeof departure.timestamp === 'string'
                      ? new Date(departure.timestamp).toLocaleString()
                      : 'Unknown'}
                  </TableCell>
                  <TableCell sx={{ color: '#000000' }}>{departure.destination}</TableCell>
                  <TableCell sx={{ color: '#000000' }}>{departure.minutes} min</TableCell>
                  <TableCell sx={{ color: '#000000' }}>Platform {departure.platform}</TableCell>
                  <TableCell sx={{ color: '#000000' }}>{departure.direction}</TableCell>
                  <TableCell sx={{ color: '#000000' }}>{departure.length} cars</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* Delay Chart */}
      <Paper sx={{ p: 2, backgroundColor: '#ffffff' }}>
        <Typography variant="h6" sx={{ color: '#000000' }} gutterBottom>
          Delays Over Time
        </Typography>
        <Box sx={{ height: 300 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={delayData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="delay" fill="#8884d8" name="Delay (minutes)" />
            </BarChart>
          </ResponsiveContainer>
        </Box>
      </Paper>
    </Container>
  );
}

export default BartAnalytics; 