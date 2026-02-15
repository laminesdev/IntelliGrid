"""
Impact Analyzer for calculating environmental and financial impact.
"""
import pandas as pd
from typing import Dict
from src.data.models import ImpactMetrics, SimulationResult
from src.utils.config import (
    CO2_FACTOR, TREES_PER_TON_CO2, WATER_FACTOR, 
    NOX_FACTOR, SO2_FACTOR, PM10_FACTOR,
    KM_PER_KG_CO2_CAR, KM_PER_KG_CO2_BUS,
    PRICING, GRID_EXPORT_PRICE
)


class ImpactAnalyzer:
    """Analyzes environmental and financial impact of the energy management system.
    
    Calculates:
    - Waste reduction (solar energy utilization improvement)
    - Financial savings (daily, yearly, and 10-year projections)
    - ROI and payback period estimates
    - CO2 emissions reduction
    - Tree equivalent (environmental offset)
    - Water savings (liters saved)
    - Air quality improvements (NOx, SO2, PM10)
    - Transport equivalence (km driven)
    - Energy independence metrics
    """
    
    # Constants for financial calculations
    BATTERY_COST = 1200000  # DZD - Approximate cost for 13.5 kWh battery + installation
    INFLATION_RATE = 0.03  # 3% annual inflation on electricity prices
    SYSTEM_LIFESPAN = 10  # Years for ROI calculation
    
    def __init__(self, simulation_result: SimulationResult):
        """Initialize analyzer with simulation results.
        
        Args:
            simulation_result: Complete simulation data
        """
        self.result = simulation_result
        self.df = pd.DataFrame(simulation_result.to_dict())
        
    def calculate_all_metrics(self) -> ImpactMetrics:
        """Calculate all impact metrics.
        
        Returns:
            ImpactMetrics with complete analysis
        """
        waste_metrics = self._calculate_waste_reduction()
        financial_metrics = self._calculate_financial_savings()
        environmental_metrics = self._calculate_environmental_impact()
        
        return ImpactMetrics(
            # Waste metrics
            wasted_without_system=waste_metrics["wasted_without"],
            wasted_with_system=waste_metrics["wasted_with"],
            waste_reduction_percent=waste_metrics["reduction_percent"],
            
            # Financial metrics
            daily_cost_without_battery=financial_metrics["cost_without"],
            daily_cost_with_battery=financial_metrics["cost_with"],
            daily_savings=financial_metrics["daily_savings"],
            yearly_savings=financial_metrics["yearly_savings"],
            ten_year_savings=financial_metrics["ten_year_savings"],
            roi_percent=financial_metrics["roi_percent"],
            payback_years=financial_metrics["payback_years"],
            export_revenue_daily=financial_metrics["export_revenue_daily"],
            export_revenue_yearly=financial_metrics["export_revenue_yearly"],
            
            # Environmental metrics
            co2_reduced_tons=environmental_metrics["co2_tons"],
            trees_equivalent=environmental_metrics["trees"],
            energy_saved_kwh=environmental_metrics["energy_saved"],
            
            # Enhanced environmental metrics
            water_saved_liters=environmental_metrics["water_liters"],
            nox_reduced_kg=environmental_metrics["nox_kg"],
            so2_reduced_kg=environmental_metrics["so2_kg"],
            pm10_reduced_kg=environmental_metrics["pm10_kg"],
            
            # Transport equivalence
            car_km_equivalent=environmental_metrics["car_km"],
            bus_km_equivalent=environmental_metrics["bus_km"],
            
            # Energy independence
            grid_independence_percent=environmental_metrics["grid_independence"]
        )
    
    def _calculate_waste_reduction(self) -> Dict:
        """Calculate solar energy waste reduction.
        
        Without the system, ~35% of solar energy is wasted (no battery storage).
        With the system, excess solar charges the battery or is exported.
        
        Returns:
            Dictionary with waste metrics
        """
        total_solar = self.result.total_solar
        total_consumption = self.result.total_consumption
        
        # Baseline waste: 35% of solar goes unused without battery
        wasted_without = total_solar * 0.35
        
        # Actual waste: Solar that couldn't be used or stored
        # This is solar_export minus any grid export value
        actual_solar_used = min(total_solar, total_consumption + self._get_battery_throughput())
        wasted_with = max(0, total_solar - actual_solar_used)
        
        # Calculate reduction percentage
        if wasted_without > 0:
            reduction_percent = ((wasted_without - wasted_with) / wasted_without) * 100
        else:
            reduction_percent = 0.0
        
        return {
            "wasted_without": round(wasted_without, 2),
            "wasted_with": round(wasted_with, 2),
            "reduction_percent": round(reduction_percent, 1)
        }
    
    def _calculate_financial_savings(self) -> Dict:
        """Calculate financial impact with enhanced projections.
        
        Compares costs with and without battery storage.
        Includes export revenue, ROI, and payback period.
        
        Returns:
            Dictionary with financial metrics
        """
        # Cost with battery system
        cost_with = self.result.total_cost
        
        # Cost without battery (baseline scenario)
        cost_without = 0.0
        for _, row in self.df.iterrows():
            # Without battery, all consumption not met by solar comes from grid
            grid_needed = max(0, row['consumption'] - row['solar_production'])
            cost_without += grid_needed * row['grid_price']
        
        # Calculate daily savings
        daily_savings = cost_without - cost_with
        
        # Export revenue (benefit from selling excess solar)
        export_revenue_daily = self.result.total_grid_export * GRID_EXPORT_PRICE
        
        # Yearly projections
        yearly_savings = daily_savings * 365
        yearly_export_revenue = export_revenue_daily * 365
        total_yearly_benefit = yearly_savings + yearly_export_revenue
        
        # 10-year projection with inflation
        # Year 1: total_yearly_benefit
        # Year 2: total_yearly_benefit * (1 + 0.03)
        # etc.
        ten_year_savings = 0.0
        for year in range(1, 11):
            ten_year_savings += total_yearly_benefit * ((1 + self.INFLATION_RATE) ** (year - 1))
        
        # ROI calculation
        roi_percent = ((ten_year_savings - self.BATTERY_COST) / self.BATTERY_COST) * 100
        
        # Payback period (years to recover battery cost)
        if total_yearly_benefit > 0:
            payback_years = self.BATTERY_COST / total_yearly_benefit
        else:
            payback_years = float('inf')
        
        return {
            "cost_without": round(cost_without, 2),
            "cost_with": round(cost_with, 2),
            "daily_savings": round(daily_savings, 2),
            "yearly_savings": round(yearly_savings, 2),
            "ten_year_savings": round(ten_year_savings, 2),
            "roi_percent": round(roi_percent, 1),
            "payback_years": round(payback_years, 1),
            "export_revenue_daily": round(export_revenue_daily, 2),
            "export_revenue_yearly": round(yearly_export_revenue, 2)
        }
    
    def _calculate_environmental_impact(self) -> Dict:
        """Calculate environmental impact with enhanced metrics.
        
        Converts energy savings to CO2, water, air quality, and transport metrics.
        
        Returns:
            Dictionary with environmental metrics
        """
        # Energy saved = difference between grid usage with and without battery
        baseline_grid = 0.0
        for _, row in self.df.iterrows():
            grid_needed = max(0, row['consumption'] - row['solar_production'])
            baseline_grid += grid_needed
        
        actual_grid = self.result.total_grid_usage
        energy_saved_daily = baseline_grid - actual_grid
        energy_saved_yearly = energy_saved_daily * 365
        
        # CO2 reduction calculation
        # Yearly CO2 saved
        yearly_co2_kg = energy_saved_yearly * CO2_FACTOR
        co2_tons = yearly_co2_kg / 1000
        
        # Tree equivalent (trees needed to offset same CO2)
        trees = co2_tons * TREES_PER_TON_CO2
        
        # Water savings (liters per year)
        # Thermal power plants use water for cooling
        water_liters = energy_saved_yearly * WATER_FACTOR
        
        # Air quality improvements (kg per year)
        nox_kg = energy_saved_yearly * NOX_FACTOR
        so2_kg = energy_saved_yearly * SO2_FACTOR
        pm10_kg = energy_saved_yearly * PM10_FACTOR
        
        # Transport equivalence (km per year)
        car_km = yearly_co2_kg * KM_PER_KG_CO2_CAR
        bus_km = yearly_co2_kg * KM_PER_KG_CO2_BUS
        
        # Grid independence (percentage reduction in grid usage)
        if baseline_grid > 0:
            grid_independence = ((baseline_grid - actual_grid) / baseline_grid) * 100
        else:
            grid_independence = 0.0
        
        return {
            "energy_saved": round(energy_saved_daily, 2),
            "daily_co2_kg": round(energy_saved_daily * CO2_FACTOR, 2),
            "co2_tons": round(co2_tons, 2),
            "trees": round(trees, 0),
            "water_liters": round(water_liters, 0),
            "nox_kg": round(nox_kg, 3),
            "so2_kg": round(so2_kg, 3),
            "pm10_kg": round(pm10_kg, 3),
            "car_km": round(car_km, 0),
            "bus_km": round(bus_km, 0),
            "grid_independence": round(grid_independence, 1)
        }
    
    def _get_battery_throughput(self) -> float:
        """Calculate total battery charge/discharge throughput.
        
        Returns:
            Total energy throughput in kWh
        """
        throughput = 0.0
        prev_level = self.df['battery_level'].iloc[0] if len(self.df) > 0 else 0
        
        for _, row in self.df.iterrows():
            current_level = row['battery_level']
            change = abs(current_level - prev_level)
            throughput += change
            prev_level = current_level
        
        return throughput
    
    def get_summary_dict(self) -> Dict:
        """Get all metrics as a flat dictionary for UI display.
        
        Returns:
            Dictionary with formatted metrics
        """
        metrics = self.calculate_all_metrics()
        
        return {
            # Waste metrics
            "waste_reduction_percent": f"{metrics.waste_reduction_percent}%",
            "wasted_without": f"{metrics.wasted_without_system:.1f} kWh",
            "wasted_with": f"{metrics.wasted_with_system:.1f} kWh",
            
            # Financial metrics
            "daily_cost_without": f"{metrics.daily_cost_without_battery:.2f} DZD",
            "daily_cost_with": f"{metrics.daily_cost_with_battery:.2f} DZD",
            "daily_savings": f"{metrics.daily_savings:.2f} DZD",
            "yearly_savings": f"{metrics.yearly_savings:,.0f} DZD",
            "ten_year_savings": f"{metrics.ten_year_savings:,.0f} DZD",
            "roi_percent": f"{metrics.roi_percent:.1f}%",
            "payback_years": f"{metrics.payback_years:.1f} years",
            "export_revenue_daily": f"{metrics.export_revenue_daily:.2f} DZD",
            "export_revenue_yearly": f"{metrics.export_revenue_yearly:,.0f} DZD",
            
            # Environmental metrics
            "co2_reduced": f"{metrics.co2_reduced_tons:.2f} tons/year",
            "trees_equivalent": f"{int(metrics.trees_equivalent)} trees",
            "energy_saved": f"{metrics.energy_saved_kwh:.1f} kWh/day",
            
            # Enhanced environmental metrics
            "water_saved": f"{int(metrics.water_saved_liters):,} L/year",
            "nox_reduced": f"{metrics.nox_reduced_kg:.3f} kg/year",
            "so2_reduced": f"{metrics.so2_reduced_kg:.3f} kg/year",
            "pm10_reduced": f"{metrics.pm10_reduced_kg:.3f} kg/year",
            
            # Transport equivalence
            "car_km_equivalent": f"{int(metrics.car_km_equivalent):,} km/year",
            "bus_km_equivalent": f"{int(metrics.bus_km_equivalent):,} km/year",
            
            # Energy independence
            "grid_independence": f"{metrics.grid_independence_percent:.1f}%"
        }
