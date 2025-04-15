export interface Departure {
    station: string;
    destination: string;
    direction: string;
    minutes: number;
    platform: string;
    bike_flag: string;
    delay: number;
    retrieved_at: string;
}

export interface ApiResponse {
    status: 'success' | 'error';
    count: number;
    data: Departure[];
    message?: string;
} 