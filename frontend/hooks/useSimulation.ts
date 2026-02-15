"use client"

import { useState, useCallback } from 'react';
import { 
  runSimulation, 
  runOptimization, 
  compareOptimizations,
  getWeatherAlerts,
  calculateImpact,
  SimulationConfig,
  SimulationResponse,
  WeatherAlertResponse,
  ImpactMetrics
} from '@/lib/api';

export interface SimulationState {
  data: SimulationResponse | null;
  loading: boolean;
  error: string | null;
}

export interface ComparisonState {
  ruleData: SimulationResponse | null;
  milpData: SimulationResponse | null;
  costSavings: number;
  improvementPercent: number;
  differentDecisionsCount: number;
  loading: boolean;
  error: string | null;
}

export function useSimulation() {
  const [simulation, setSimulation] = useState<SimulationState>({
    data: null,
    loading: false,
    error: null,
  });

  const [comparison, setComparison] = useState<ComparisonState>({
    ruleData: null,
    milpData: null,
    costSavings: 0,
    improvementPercent: 0,
    differentDecisionsCount: 0,
    loading: false,
    error: null,
  });

  const [alerts, setAlerts] = useState<WeatherAlertResponse | null>(null);
  const [impact, setImpact] = useState<ImpactMetrics | null>(null);

  const simulate = useCallback(async (config: SimulationConfig) => {
    setSimulation({ data: null, loading: true, error: null });
    try {
      const data = config.mode === 'milp' 
        ? await runOptimization(config)
        : await runSimulation(config);
      setSimulation({ data, loading: false, error: null });
      
      // Fetch impact metrics
      const impactData = await calculateImpact(data);
      setImpact(impactData.metrics);
      
      // Fetch weather alerts
      const lastHour = data.hourly_data[data.hourly_data.length - 1];
      const alertData = await getWeatherAlerts({
        tomorrow_weather: config.tomorrow_weather || config.weather,
        battery_soc: lastHour.battery_soc,
        current_hour: lastHour.hour,
      });
      setAlerts(alertData);
      
      return data;
    } catch (err) {
      const error = err instanceof Error ? err.message : 'Simulation failed';
      setSimulation({ data: null, loading: false, error });
      throw err;
    }
  }, []);

  const compare = useCallback(async (config: SimulationConfig) => {
    setComparison({
      ruleData: null,
      milpData: null,
      costSavings: 0,
      improvementPercent: 0,
      differentDecisionsCount: 0,
      loading: true,
      error: null,
    });
    
    try {
      const data = await compareOptimizations(config);
      setComparison({
        ruleData: data.rule_result,
        milpData: data.milp_result,
        costSavings: data.cost_savings,
        improvementPercent: data.improvement_percent,
        differentDecisionsCount: data.different_decisions_count,
        loading: false,
        error: null,
      });
      return data;
    } catch (err) {
      const error = err instanceof Error ? err.message : 'Comparison failed';
      setComparison(prev => ({ ...prev, loading: false, error }));
      throw err;
    }
  }, []);

  const reset = useCallback(() => {
    setSimulation({ data: null, loading: false, error: null });
    setComparison({
      ruleData: null,
      milpData: null,
      costSavings: 0,
      improvementPercent: 0,
      loading: false,
      error: null,
    });
    setAlerts(null);
    setImpact(null);
  }, []);

  return {
    simulation,
    comparison,
    alerts,
    impact,
    simulate,
    compare,
    reset,
  };
}
