export interface Departure {
    destination: string;
    direction: string;
    minutes: number;
    platform: string;
    bike_flag: boolean;
    delay: number;
    color: string;
    length: number;
}

export interface ApiResponse {
    status: 'success' | 'error';
    count: number;
    data: Departure[];
    message?: string;
} 