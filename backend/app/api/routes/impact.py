"""
Impact analysis routes.
"""
from fastapi import APIRouter, HTTPException
import traceback

from app.models import SimulationResponse, ImpactResponse, ImpactMetrics
from src.analysis.impact_analyzer import ImpactAnalyzer
from src.data.models import SimulationResult as CoreSimulationResult, HourlyData as CoreHourlyData, Action
from app.logging_config import logger

router = APIRouter()


@router.post("/impact", response_model=ImpactResponse)
async def calculate_impact(simulation_data: SimulationResponse):
    """
    Calculate environmental and financial impact.
    
    Analyzes simulation results to calculate:
    - Solar waste reduction
    - CO2 emissions reduction
    - Tree equivalent
    - Daily/yearly savings
    
    Args:
        simulation_data: Results from /simulate endpoint
        
    Returns:
        Impact metrics with formatted values
    """
    try:
        # Convert API model to core model
        core_result = CoreSimulationResult()
        core_result.seed = simulation_data.seed
        
        for h in simulation_data.hourly_data:
            # Map action string back to Action enum
            action_map = {
                'charge_battery': Action.CHARGE_BATTERY,
                'discharge_battery': Action.DISCHARGE_BATTERY,
                'sell_to_grid': Action.SELL_TO_GRID,
                'use_grid': Action.USE_GRID,
                'idle': Action.IDLE
            }
            action = action_map.get(h.action, Action.IDLE)
            
            core_hourly = CoreHourlyData(
                hour=h.hour,
                solar_production=h.solar_production,
                consumption=h.consumption,
                battery_level=h.battery_level,
                battery_soc=h.battery_soc,
                grid_usage=h.grid_usage,
                grid_export=h.grid_export,
                net_energy=h.net_energy,
                action=action,
                grid_price=h.grid_price,
                cost=h.cost,
                savings=h.savings
            )
            core_result.hourly_data.append(core_hourly)
        
        core_result.total_solar = simulation_data.total_solar
        core_result.total_consumption = simulation_data.total_consumption
        core_result.total_grid_usage = simulation_data.total_grid_usage
        core_result.total_grid_export = simulation_data.total_grid_export
        core_result.total_cost = simulation_data.total_cost
        core_result.total_savings = simulation_data.total_savings
        
        # Calculate impact
        analyzer = ImpactAnalyzer(core_result)
        metrics = analyzer.calculate_all_metrics()
        summary = analyzer.get_summary_dict()
        
        return ImpactResponse(
            metrics=ImpactMetrics(
                # Waste metrics
                waste_reduction_percent=summary['waste_reduction_percent'],
                wasted_without=summary['wasted_without'],
                wasted_with=summary['wasted_with'],
                # Financial metrics
                daily_cost_without=summary['daily_cost_without'],
                daily_cost_with=summary['daily_cost_with'],
                daily_savings=summary['daily_savings'],
                yearly_savings=summary['yearly_savings'],
                ten_year_savings=summary['ten_year_savings'],
                roi_percent=summary['roi_percent'],
                payback_years=summary['payback_years'],
                export_revenue_daily=summary['export_revenue_daily'],
                export_revenue_yearly=summary['export_revenue_yearly'],
                # Environmental metrics
                co2_reduced=summary['co2_reduced'],
                trees_equivalent=summary['trees_equivalent'],
                energy_saved=summary['energy_saved'],
                # Enhanced environmental metrics
                water_saved=summary['water_saved'],
                nox_reduced=summary['nox_reduced'],
                so2_reduced=summary['so2_reduced'],
                pm10_reduced=summary['pm10_reduced'],
                # Transport equivalence
                car_km_equivalent=summary['car_km_equivalent'],
                bus_km_equivalent=summary['bus_km_equivalent'],
                # Energy independence
                grid_independence=summary['grid_independence']
            )
        )
        
    except Exception as e:
        logger.error(f"Error in impact calculation: {e}")
        logger.debug(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
