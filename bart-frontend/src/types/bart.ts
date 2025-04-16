export interface Station {
  name: string;
  abbr: string;
  // Optional fields that might not be available from the database
  address?: string;
  city?: string;
  county?: string;
  state?: string;
  zipcode?: string;
}

export interface Departure {
    destination: string;
    direction: string;
    minutes: number;
    platform: string;
    bike_flag: boolean;
    delay: number;
    color: string;
    length: number;
    timestamp?: string;
}

export interface ApiResponse {
    status: 'success' | 'error';
    count: number;
    data: Departure[];
    message?: string;
} 