import axios from 'axios';
import { SimulationConfig, SimulationResult, Alert, WeatherAlertRequest, WeatherAlertResponse, ImpactMetrics } from '@/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for debugging
api.interceptors.request.use(
  (config) => {
    console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`, config.data);
    return config;
  },
  (error) => {
    console.error('[API Request Error]', error);
    return Promise.reject(error);
  }
);

// Response interceptor for debugging
api.interceptors.response.use(
  (response) => {
    console.log(`[API Response] ${response.config.method?.toUpperCase()} ${response.config.url} - ${response.status}`);
    return response;
  },
  (error) => {
    console.error('[API Response Error]', {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      data: error.response?.data,
      message: error.message,
    });
    return Promise.reject(error);
  }
);

export const runSimulation = async (config: SimulationConfig): Promise<SimulationResult> => {
  const { data } = await api.post('/api/v1/simulate', config);
  return data;
};

export const runOptimization = async (config: SimulationConfig): Promise<SimulationResult> => {
  const { data } = await api.post('/api/v1/optimize', config);
  return data;
};

export const compareOptimizations = async (config: SimulationConfig) => {
  const { data } = await api.post('/api/v1/compare', config);
  return data;
};

export const getWeatherAlerts = async (request: WeatherAlertRequest): Promise<WeatherAlertResponse> => {
  const { data } = await api.post('/api/v1/weather/alerts', request);
  return data;
};

export const calculateImpact = async (simulationData: SimulationResult): Promise<{ metrics: ImpactMetrics }> => {
  const { data } = await api.post('/api/v1/impact', simulationData);
  return data;
};

export default api;
