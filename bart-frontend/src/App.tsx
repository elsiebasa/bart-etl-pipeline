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
  Box,
  Tabs,
  Tab
} from '@mui/material';
import { Departure, Station } from './types/bart';
import { getDepartures, getStations, getStationAnalytics } from './services/bartService';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

function App() {
  const [departures, setDepartures] = useState<Departure[]>([]);
  const [stations, setStations] = useState<Station[]>([]);
  const [selectedStation, setSelectedStation] = useState<string>('12th');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [tabValue, setTabValue] = useState(0);
  const [historicalData, setHistoricalData] = useState<any[]>([]);
  const [historicalLoading, setHistoricalLoading] = useState(false);
  const [historicalError, setHistoricalError] = useState<string | null>(null);

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
        setLastUpdated(new Date());
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

  // Load historical data when station is selected and historical tab is active
  useEffect(() => {
    const loadHistoricalData = async () => {
      if (!selectedStation || tabValue !== 1) return;
      
      try {
        setHistoricalLoading(true);
        setHistoricalError(null);
        const stats = await getStationAnalytics();
        setHistoricalData(stats);
      } catch (err) {
        console.error('Failed to fetch historical data:', err);
        setHistoricalError('Failed to load historical data. Please try again later.');
      } finally {
        setHistoricalLoading(false);
      }
    };

    loadHistoricalData();
  }, [selectedStation, tabValue]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const getColorStyle = (color: string) => {
    const colorMap: { [key: string]: string } = {
      'YELLOW': '#ffff33',
      'ORANGE': '#ff9933',
      'BLUE': '#0099cc',
      'GREEN': '#009933',
      'RED': '#cc0000',
      'WHITE': '#ffffff',
      'BLACK': '#000000'
    };
    return {
      backgroundColor: colorMap[color] || '#f0f0f0',
      color: '#000000',
      fontWeight: 'bold',
      border: '1px solid rgba(0, 0, 0, 0.2)'
    };
  };

  const getDirectionStyle = (direction: string) => {
    const directionMap: { [key: string]: { color: string, backgroundColor: string } } = {
      'North': { color: '#000000', backgroundColor: '#a8d8ea' },
      'South': { color: '#000000', backgroundColor: '#ffb6b6' },
      'East': { color: '#000000', backgroundColor: '#b5ead7' },
      'West': { color: '#000000', backgroundColor: '#ffdac1' }
    };
    return directionMap[direction] || { color: '#000000', backgroundColor: '#f0f0f0' };
  };

  const formatLastUpdated = (date: Date | null) => {
    if (!date) return '';
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: true
    });
  };

  const selectedStationInfo = stations.find(s => s.abbr === selectedStation);

  const calculateAverageDelay = () => {
    const delayedTrains = departures.filter(d => d.delay > 0);
    if (delayedTrains.length === 0) return 0;
    const totalDelay = delayedTrains.reduce((sum, d) => sum + d.delay, 0);
    return (totalDelay / delayedTrains.length).toFixed(1);
  };

  const calculateMaxDelay = () => {
    if (departures.length === 0) return 0;
    return Math.max(...departures.map(d => d.delay));
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        BART Departures
      </Typography>
      <Typography variant="subtitle1" color="text.secondary" sx={{ mb: 4 }}>
        Real-time BART train departures and arrivals. Select a station to view upcoming trains, 
        including destination, direction, and estimated times. Data updates every 30 seconds.
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

      {selectedStationInfo && (
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle1">
            {selectedStationInfo.name} Station • {selectedStationInfo.city}
          </Typography>
        </Box>
      )}

      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tabValue} onChange={handleTabChange} aria-label="BART data tabs">
          <Tab label="Live Departures" />
          <Tab label="Historical Data" />
        </Tabs>
      </Box>

      <TabPanel value={tabValue} index={0}>
        {loading ? (
          <Box display="flex" justifyContent="center" my={4}>
            <CircularProgress />
          </Box>
        ) : error ? (
          <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>
        ) : (
          <>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
              <Typography variant="body2" color="text.secondary">
                Last updated: {formatLastUpdated(lastUpdated)}
              </Typography>
              <Box>
                <Typography variant="body2" color="text.secondary" sx={{ display: 'inline', mr: 2 }}>
                  Average Delay: {calculateAverageDelay()} min
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ display: 'inline' }}>
                  Max Delay: {calculateMaxDelay()} min
                </Typography>
              </Box>
            </Box>
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Destination</TableCell>
                    <TableCell>Direction</TableCell>
                    <TableCell>Arrival Time</TableCell>
                    <TableCell>Departure Time</TableCell>
                    <TableCell>Minutes</TableCell>
                    <TableCell>Platform</TableCell>
                    <TableCell>Train Info</TableCell>
                    <TableCell>Bikes</TableCell>
                    <TableCell>Delay</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {departures.map((departure, index) => {
                    const now = new Date();
                    const arrivalTime = new Date(now.getTime() + departure.minutes * 60000);
                    const departureTime = new Date(arrivalTime.getTime() - 2 * 60000);
                    
                    return (
                      <TableRow key={index}>
                        <TableCell>
                          <Typography variant="h6" component="div" sx={{ fontWeight: 'bold' }}>
                            {departure.destination}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={departure.direction}
                            style={getDirectionStyle(departure.direction)}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          {arrivalTime.toLocaleTimeString('en-US', {
                            hour: '2-digit',
                            minute: '2-digit',
                            hour12: true
                          })}
                        </TableCell>
                        <TableCell>
                          {departureTime.toLocaleTimeString('en-US', {
                            hour: '2-digit',
                            minute: '2-digit',
                            hour12: true
                          })}
                        </TableCell>
                        <TableCell>{departure.minutes}</TableCell>
                        <TableCell>{departure.platform}</TableCell>
                        <TableCell>
                          <Chip 
                            label={`${departure.color || 'Unknown'} - ${departure.length} cars`}
                            style={getColorStyle(departure.color || 'WHITE')}
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
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </TableContainer>
          </>
        )}
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        <Typography variant="h6" gutterBottom>
          Historical Performance (Last 5 Days)
        </Typography>
        {historicalLoading ? (
          <Box display="flex" justifyContent="center" my={4}>
            <CircularProgress />
          </Box>
        ) : historicalError ? (
          <Alert severity="error" sx={{ mb: 2 }}>
            {historicalError}
          </Alert>
        ) : historicalData.length === 0 ? (
          <Alert severity="info" sx={{ mb: 2 }}>
            No historical data available for this station.
          </Alert>
        ) : (
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Destination</TableCell>
                  <TableCell>Total Departures</TableCell>
                  <TableCell>Delayed Trains</TableCell>
                  <TableCell>Average Delay (min)</TableCell>
                  <TableCell>Max Delay (min)</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {historicalData.map((data, index) => (
                  <TableRow key={index}>
                    <TableCell>
                      <Typography variant="subtitle1">
                        {data.destination || 'All Destinations'}
                      </Typography>
                    </TableCell>
                    <TableCell>{data.total_departures || 0}</TableCell>
                    <TableCell>{data.delay_count || 0}</TableCell>
                    <TableCell>
                      {data.avg_delay_minutes ? data.avg_delay_minutes.toFixed(1) : '0'}
                    </TableCell>
                    <TableCell>
                      {data.max_delay_minutes ? data.max_delay_minutes.toFixed(1) : '0'}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </TabPanel>
    </Container>
  );
}

export default App;
