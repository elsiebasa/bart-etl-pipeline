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
  Chip,
  Box
} from '@mui/material';
import { Departure, Station } from '../types/bart';
import { getDepartures, getStations } from '../services/bartService';

function DepartureBoard() {
  const [departures, setDepartures] = useState<Departure[]>([]);
  const [stations, setStations] = useState<Station[]>([]);
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
          setSelectedStation(stationList[0].abbr);
        }
      } catch (err) {
        setError('Failed to load stations');
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

  const selectedStationInfo = stations.find(s => s.abbr === selectedStation);

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
            <MenuItem key={station.abbr} value={station.abbr}>
              {station.name} ({station.abbr})
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      {selectedStationInfo && selectedStationInfo.address && (
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle1">
            {selectedStationInfo.address}
            {selectedStationInfo.city && `, ${selectedStationInfo.city}`}
            {selectedStationInfo.state && `, ${selectedStationInfo.state}`}
            {selectedStationInfo.zipcode && ` ${selectedStationInfo.zipcode}`}
          </Typography>
        </Box>
      )}

      {loading ? (
        <Box display="flex" justifyContent="center" my={4}>
          <CircularProgress />
        </Box>
      ) : error ? (
        <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>
      ) : departures.length === 0 ? (
        <Alert severity="info" sx={{ mb: 2 }}>No departures found for this station.</Alert>
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
                <TableCell>Time</TableCell>
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
                      label={`${departure.color || 'Unknown'} - ${departure.length || '?'} cars`}
                      style={getColorStyle(departure.color || '')}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{departure.bike_flag ? 'Yes' : 'No'}</TableCell>
                  <TableCell>
                    {departure.delay > 0 ? (
                      <Chip 
                        label={`${departure.delay} min delay`}
                        color="error"
                        size="small"
                      />
                    ) : (
                      <Chip 
                        label="On time"
                        color="success"
                        size="small"
                      />
                    )}
                  </TableCell>
                  <TableCell>
                    {departure.timestamp ? new Date(departure.timestamp).toLocaleTimeString() : 'N/A'}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Container>
  );
}

export default DepartureBoard; 