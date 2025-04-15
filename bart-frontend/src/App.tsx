import React, { useEffect, useState } from 'react';
import { 
  Container, 
  Typography, 
  Select, 
  MenuItem, 
  FormControl, 
  InputLabel,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  CircularProgress,
  Alert
} from '@mui/material';
import { Departure } from './types/bart';
import { fetchDepartures } from './services/bartService';

function App() {
  const [departures, setDepartures] = useState<Departure[]>([]);
  const [selectedStation, setSelectedStation] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Get unique stations from departures
  const stations = Array.from(new Set(departures.map(d => d.station))).sort();

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const response = await fetchDepartures();
        setDepartures(response.data);
        setError(null);
      } catch (err) {
        setError('Failed to fetch departure data');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    loadData();
    // Refresh data every 30 seconds
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, []);

  // Filter departures by selected station
  const filteredDepartures = selectedStation
    ? departures.filter(d => d.station === selectedStation)
    : departures;

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        BART Departures
      </Typography>

      <FormControl fullWidth sx={{ mb: 4 }}>
        <InputLabel id="station-select-label">Select Station</InputLabel>
        <Select
          labelId="station-select-label"
          value={selectedStation}
          label="Select Station"
          onChange={(e) => setSelectedStation(e.target.value)}
        >
          <MenuItem value="">
            <em>All Stations</em>
          </MenuItem>
          {stations.map((station) => (
            <MenuItem key={station} value={station}>
              {station}
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      {loading ? (
        <CircularProgress />
      ) : error ? (
        <Alert severity="error">{error}</Alert>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Station</TableCell>
                <TableCell>Destination</TableCell>
                <TableCell>Direction</TableCell>
                <TableCell>Minutes</TableCell>
                <TableCell>Platform</TableCell>
                <TableCell>Bikes</TableCell>
                <TableCell>Delay</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredDepartures.map((departure, index) => (
                <TableRow key={index}>
                  <TableCell>{departure.station}</TableCell>
                  <TableCell>{departure.destination}</TableCell>
                  <TableCell>{departure.direction}</TableCell>
                  <TableCell>{departure.minutes}</TableCell>
                  <TableCell>{departure.platform}</TableCell>
                  <TableCell>{departure.bike_flag}</TableCell>
                  <TableCell>{departure.delay}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Container>
  );
}

export default App;
