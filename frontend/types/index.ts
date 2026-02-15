export interface HourlyData {
  hour: number;
  solar_production: number;
  consumption: number;
  battery_level: number;
  battery_soc: number;
  grid_usage: number;
  grid_export: number;
  net_energy: number;
  action: string;
  grid_price: number;
  cost: number;
  savings: number;
}

export interface SimulationResult {
  hourly_data: HourlyData[];
  total_solar: number;
  total_consumption: number;
  total_grid_usage: number;
  total_grid_export: number;
  total_cost: number;
  total_savings: number;
  seed?: number;
}

export interface SimulationConfig {
  season: 'summer' | 'winter';
  weather: 'sunny' | 'partly_cloudy' | 'cloudy' | 'rainy';
  day_type: 'weekday' | 'weekend';
  tomorrow_weather?: 'sunny' | 'partly_cloudy' | 'cloudy' | 'rainy' | null;
  seed?: number;
  mode: 'rule' | 'milp';
}

export interface Alert {
  type: 'success' | 'warning' | 'danger' | 'info';
  message: string;
  priority: number;
  recommendation: string;
  icon: string;
}

export interface WeatherAlertRequest {
  tomorrow_weather?: 'sunny' | 'partly_cloudy' | 'cloudy' | 'rainy' | null;
  battery_soc: number;
  current_hour: number;
}

export interface WeatherAlertResponse {
  alerts: Alert[];
  status: string;
}

export interface ImpactMetrics {
  // Waste metrics
  waste_reduction_percent: string;
  wasted_without: string;
  wasted_with: string;
  
  // Financial metrics
  daily_cost_without: string;
  daily_cost_with: string;
  daily_savings: string;
  yearly_savings: string;
  ten_year_savings: string;
  roi_percent: string;
  payback_years: string;
  export_revenue_daily: string;
  export_revenue_yearly: string;
  
  // Environmental metrics
  co2_reduced: string;
  trees_equivalent: string;
  energy_saved: string;
  
  // Enhanced environmental metrics
  water_saved: string;
  nox_reduced: string;
  so2_reduced: string;
  pm10_reduced: string;
  
  // Transport equivalence
  car_km_equivalent: string;
  bus_km_equivalent: string;
  
  // Energy independence
  grid_independence: string;
}
