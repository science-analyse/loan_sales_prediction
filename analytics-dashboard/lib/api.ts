import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Type definitions for API responses
export interface KPIData {
  metric: string;
  value: number;
  change: number;
  trend: 'up' | 'down' | 'neutral';
}

export interface TimeSeriesPoint {
  quarter: string;
  value: number;
  [key: string]: any;
}

export interface OverviewData {
  kpis: KPIData[];
  trends: TimeSeriesPoint[];
}

export interface EconomicIndicator {
  quarter: string;
  gdp_growth: number;
  inflation: number;
  unemployment: number;
  oil_price: number;
  exchange_rate: number;
}

export interface BankingMetric {
  quarter: string;
  loan_sales: number;
  npl_ratio: number;
  roa: number;
  customer_count: number;
  deposits: number;
}

export interface QuarterlyData {
  quarter: string;
  loan_sales: number;
  gdp_growth: number;
  inflation: number;
  npl_ratio: number;
  roa: number;
  customer_count: number;
}

export interface ForecastPoint {
  quarter: string;
  predicted: number;
  lower_bound?: number;
  upper_bound?: number;
  actual?: number;
}

export interface SimpleForecast {
  historical: ForecastPoint[];
  forecast: ForecastPoint[];
}

export interface CorrelationData {
  variables: string[];
  matrix: number[][];
}

// API service functions
export const analyticsApi = {
  // Get overview data
  async getOverview(): Promise<OverviewData> {
    try {
      const response = await api.get('/api/analytics/overview');
      return response.data;
    } catch (error) {
      console.error('Error fetching overview data:', error);
      throw error;
    }
  },

  // Get economic indicators
  async getEconomicIndicators(): Promise<EconomicIndicator[]> {
    try {
      const response = await api.get('/api/analytics/economic-indicators');
      return response.data;
    } catch (error) {
      console.error('Error fetching economic indicators:', error);
      throw error;
    }
  },

  // Get banking metrics
  async getBankingMetrics(): Promise<BankingMetric[]> {
    try {
      const response = await api.get('/api/analytics/banking-metrics');
      return response.data;
    } catch (error) {
      console.error('Error fetching banking metrics:', error);
      throw error;
    }
  },

  // Get quarterly data
  async getQuarterlyData(): Promise<QuarterlyData[]> {
    try {
      const response = await api.get('/api/analytics/quarterly');
      return response.data;
    } catch (error) {
      console.error('Error fetching quarterly data:', error);
      throw error;
    }
  },

  // Get simple forecast
  async getSimpleForecast(): Promise<SimpleForecast> {
    try {
      const response = await api.get('/api/predictions/simple-forecast');
      return response.data;
    } catch (error) {
      console.error('Error fetching forecast data:', error);
      throw error;
    }
  },

  // Get correlation matrix
  async getCorrelations(): Promise<CorrelationData> {
    try {
      const response = await api.get('/api/analytics/correlations');
      return response.data;
    } catch (error) {
      console.error('Error fetching correlation data:', error);
      throw error;
    }
  },
};

// Utility functions
export const formatters = {
  // Format number for Azerbaijani locale
  number: (value: number, decimals: number = 2): string => {
    return new Intl.NumberFormat('az-AZ', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    }).format(value);
  },

  // Format currency (AZN)
  currency: (value: number): string => {
    return new Intl.NumberFormat('az-AZ', {
      style: 'currency',
      currency: 'AZN',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  },

  // Format percentage
  percentage: (value: number, decimals: number = 2): string => {
    return new Intl.NumberFormat('az-AZ', {
      style: 'percent',
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    }).format(value / 100);
  },

  // Compact number format (e.g., 1.2M, 3.4K)
  compact: (value: number): string => {
    return new Intl.NumberFormat('az-AZ', {
      notation: 'compact',
      compactDisplay: 'short',
    }).format(value);
  },
};

export default api;
