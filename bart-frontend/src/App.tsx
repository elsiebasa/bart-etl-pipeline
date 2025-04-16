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
  Alert,
  Chip
} from '@mui/material';
import { Departure } from './types/bart';
import { getDepartures, getStations } from './services/bartService';

function App() {
  const [departures, setDepartures] = useState<Departure[]>([]);
  const [stations, setStations] = useState<string[]>([]);
  const [selectedStation, setSelectedStation] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load stations on component mount
  useEffect(() => {
    const loadStations = async () => {
      try {
        const stationList = await getStations();
        setStations(stationList);
        if (stationList.length > 0) {
          setSelectedStation(stationList[0]);
        }
      } catch (err) {
        setError('Failed to fetch stations');
        console.error(err);
      }
    };
    loadStations();
  }, []);

  // Load departures when station is selected
  useEffect(() => {
    const loadDepartures = async () => {
      if (!selectedStation) return;
      
      try {
        setLoading(true);
        const departureList = await getDepartures(selectedStation);
        setDepartures(departureList);
        setError(null);
      } catch (err) {
        setError('Failed to fetch departure data');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    loadDepartures();
    // Refresh data every 30 seconds
    const interval = setInterval(loadDepartures, 30000);
    return () => clearInterval(interval);
  }, [selectedStation]);

  const getColorStyle = (color: string) => {
    const colorMap: { [key: string]: string } = {
      'YELLOW': '#ffff33',
      'ORANGE': '#ff9933',
      'BLUE': '#0099cc',
      'GREEN': '#009933',
      'RED': '#cc0000'
    };
    return {
      backgroundColor: colorMap[color] || '#ffffff',
      color: color === 'YELLOW' ? '#000000' : '#ffffff',
      fontWeight: 'bold'
    };
  };

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
                <TableCell>Destination</TableCell>
                <TableCell>Direction</TableCell>
                <TableCell>Minutes</TableCell>
                <TableCell>Platform</TableCell>
                <TableCell>Train Info</TableCell>
                <TableCell>Bikes</TableCell>
                <TableCell>Delay</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {departures.map((departure, index) => (
                <TableRow key={index}>
                  <TableCell>{departure.destination}</TableCell>
                  <TableCell>{departure.direction}</TableCell>
                  <TableCell>{departure.minutes}</TableCell>
                  <TableCell>{departure.platform}</TableCell>
                  <TableCell>
                    <Chip 
                      label={`${departure.color} - ${departure.length} cars`}
                      style={getColorStyle(departure.color)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{departure.bike_flag ? 'Yes' : 'No'}</TableCell>
                  <TableCell>{departure.delay > 0 ? `${departure.delay} min` : 'On time'}</TableCell>
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
