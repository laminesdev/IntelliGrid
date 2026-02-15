"""
Simulation service - wrapper around existing core logic for FastAPI.
"""
from typing import List, Optional

from app.models import (
    SimulationConfig, SimulationResponse, HourlyData,
    Season, Weather, DayType, OptimizationMode
)

# Import existing core modules
from src.core.hybrid_adapter import HybridSimulationAdapter
from src.data.models import (
    SimulationConfig as CoreSimulationConfig,
    Season as CoreSeason,
    Weather as CoreWeather,
    DayType as CoreDayType
)
from src.engine.weather_predictor import WeatherPredictor
from src.analysis.impact_analyzer import ImpactAnalyzer


class SimulationService:
    """Service layer for running simulations."""
    
    @staticmethod
    def _convert_config(config: SimulationConfig) -> CoreSimulationConfig:
        """Convert API config to core config."""
        season_map = {
            Season.SUMMER: CoreSeason.SUMMER,
            Season.WINTER: CoreSeason.WINTER
        }
        weather_map = {
            Weather.SUNNY: CoreWeather.SUNNY,
            Weather.PARTLY_CLOUDY: CoreWeather.PARTLY_CLOUDY,
            Weather.CLOUDY: CoreWeather.CLOUDY,
            Weather.RAINY: CoreWeather.RAINY
        }
        day_type_map = {
            DayType.WEEKDAY: CoreDayType.WEEKDAY,
            DayType.WEEKEND: CoreDayType.WEEKEND
        }
        
        tomorrow = None
        if config.tomorrow_weather:
            tomorrow = weather_map.get(config.tomorrow_weather)
        
        return CoreSimulationConfig(
            season=season_map[config.season],
            weather=weather_map[config.weather],
            day_type=day_type_map[config.day_type],
            tomorrow_weather=tomorrow
        )
    
    @staticmethod
    def _convert_hourly_data(hourly) -> HourlyData:
        """Convert core HourlyData to API model."""
        return HourlyData(
            hour=hourly.hour,
            solar_production=hourly.solar_production,
            consumption=hourly.consumption,
            battery_level=hourly.battery_level,
            battery_soc=hourly.battery_soc,
            grid_usage=hourly.grid_usage,
            grid_export=hourly.grid_export,
            net_energy=hourly.net_energy,
            action=hourly.action.value if hasattr(hourly.action, 'value') else str(hourly.action),
            grid_price=hourly.grid_price,
            cost=hourly.cost,
            savings=hourly.savings
        )
    
    @classmethod
    def run_simulation(cls, config: SimulationConfig) -> SimulationResponse:
        """Run a single simulation."""
        core_config = cls._convert_config(config)
        
        # Run simulation
        adapter = HybridSimulationAdapter(
            core_config,
            seed=config.seed,
            mode=config.mode.value
        )
        result = adapter.generate_24h_data()
        
        # Convert to API response
        return SimulationResponse(
            hourly_data=[cls._convert_hourly_data(h) for h in result.hourly_data],
            total_solar=result.total_solar,
            total_consumption=result.total_consumption,
            total_grid_usage=result.total_grid_usage,
            total_grid_export=result.total_grid_export,
            total_cost=result.total_cost,
            total_savings=result.total_savings,
            seed=config.seed
        )
    
    @classmethod
    def compare_optimizations(cls, config: SimulationConfig) -> dict:
        """Compare rule-based vs MILP optimization."""
        core_config = cls._convert_config(config)
        
        # Run rule-based
        rule_adapter = HybridSimulationAdapter(core_config, seed=config.seed, mode='rule')
        rule_result = rule_adapter.generate_24h_data()
        
        # Run MILP
        milp_adapter = HybridSimulationAdapter(core_config, seed=config.seed, mode='milp')
        milp_result = milp_adapter.generate_24h_data()
        
        # Calculate differences
        cost_savings = rule_result.total_cost - milp_result.total_cost
        improvement_pct = (cost_savings / rule_result.total_cost * 100) if rule_result.total_cost != 0 else 0
        
        # Count different decisions
        different_count = sum(
            1 for r, m in zip(rule_result.hourly_data, milp_result.hourly_data)
            if r.action != m.action
        )
        
        return {
            'rule_result': SimulationResponse(
                hourly_data=[cls._convert_hourly_data(h) for h in rule_result.hourly_data],
                total_solar=rule_result.total_solar,
                total_consumption=rule_result.total_consumption,
                total_grid_usage=rule_result.total_grid_usage,
                total_grid_export=rule_result.total_grid_export,
                total_cost=rule_result.total_cost,
                total_savings=rule_result.total_savings,
                seed=config.seed
            ),
            'milp_result': SimulationResponse(
                hourly_data=[cls._convert_hourly_data(h) for h in milp_result.hourly_data],
                total_solar=milp_result.total_solar,
                total_consumption=milp_result.total_consumption,
                total_grid_usage=milp_result.total_grid_usage,
                total_grid_export=milp_result.total_grid_export,
                total_cost=milp_result.total_cost,
                total_savings=milp_result.total_savings,
                seed=config.seed
            ),
            'cost_savings': cost_savings,
            'improvement_percent': improvement_pct,
            'different_decisions_count': different_count
        }
