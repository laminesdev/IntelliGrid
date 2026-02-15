"""
Pydantic models for API requests and responses.
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class Season(str, Enum):
    SUMMER = "summer"
    WINTER = "winter"


class Weather(str, Enum):
    SUNNY = "sunny"
    PARTLY_CLOUDY = "partly_cloudy"
    CLOUDY = "cloudy"
    RAINY = "rainy"


class DayType(str, Enum):
    WEEKDAY = "weekday"
    WEEKEND = "weekend"


class OptimizationMode(str, Enum):
    RULE = "rule"
    MILP = "milp"


class SimulationConfig(BaseModel):
    """Configuration for energy simulation."""
    season: Season = Field(default=Season.SUMMER, description="Season for simulation")
    weather: Weather = Field(default=Weather.SUNNY, description="Current weather")
    day_type: DayType = Field(default=DayType.WEEKDAY, description="Type of day")
    tomorrow_weather: Optional[Weather] = Field(default=None, description="Tomorrow's forecast")
    seed: Optional[int] = Field(default=42, description="Random seed for reproducibility")
    mode: OptimizationMode = Field(default=OptimizationMode.RULE, description="Optimization mode")


class HourlyData(BaseModel):
    """Hourly simulation data point."""
    hour: int = Field(..., description="Hour of day (0-23)")
    solar_production: float = Field(..., description="Solar production in kWh")
    consumption: float = Field(..., description="Energy consumption in kWh")
    battery_level: float = Field(..., description="Battery charge level in kWh")
    battery_soc: float = Field(..., description="Battery state of charge (0-1)")
    grid_usage: float = Field(..., description="Energy imported from grid in kWh")
    grid_export: float = Field(..., description="Energy exported to grid in kWh")
    net_energy: float = Field(..., description="Net energy (solar - consumption)")
    action: str = Field(..., description="Action taken")
    grid_price: float = Field(..., description="Grid price in DZD/kWh")
    cost: float = Field(..., description="Cost for this hour")
    savings: float = Field(..., description="Savings vs no battery")


class SimulationResponse(BaseModel):
    """Response from simulation endpoint."""
    hourly_data: List[HourlyData] = Field(..., description="Hour-by-hour data")
    total_solar: float = Field(..., description="Total solar production")
    total_consumption: float = Field(..., description="Total consumption")
    total_grid_usage: float = Field(..., description="Total grid import")
    total_grid_export: float = Field(..., description="Total grid export")
    total_cost: float = Field(..., description="Total cost")
    total_savings: float = Field(..., description="Total savings")
    seed: Optional[int] = Field(None, description="Random seed used")


class Alert(BaseModel):
    """Alert model."""
    type: str = Field(..., description="Alert type: success, warning, danger, info")
    message: str = Field(..., description="Alert message")
    priority: int = Field(..., description="Priority (1-4, lower is higher)")
    recommendation: str = Field(..., description="Recommendation text")
    icon: str = Field(..., description="Icon class for the alert")


class WeatherAlertRequest(BaseModel):
    """Request for weather alerts."""
    tomorrow_weather: Optional[Weather] = Field(default=None)
    battery_soc: float = Field(..., ge=0.0, le=1.0, description="Current battery SOC")
    current_hour: int = Field(default=20, ge=0, le=23, description="Current hour")


class WeatherAlertResponse(BaseModel):
    """Response with weather alerts."""
    alerts: List[Alert] = Field(default_factory=list)
    status: str = Field(..., description="Status message")


class ImpactMetrics(BaseModel):
    """Environmental and financial impact metrics."""
    # Waste metrics
    waste_reduction_percent: str
    wasted_without: str
    wasted_with: str
    
    # Financial metrics
    daily_cost_without: str
    daily_cost_with: str
    daily_savings: str
    yearly_savings: str
    ten_year_savings: str
    roi_percent: str
    payback_years: str
    export_revenue_daily: str
    export_revenue_yearly: str
    
    # Environmental metrics
    co2_reduced: str
    trees_equivalent: str
    energy_saved: str
    
    # Enhanced environmental metrics
    water_saved: str
    nox_reduced: str
    so2_reduced: str
    pm10_reduced: str
    
    # Transport equivalence
    car_km_equivalent: str
    bus_km_equivalent: str
    
    # Energy independence
    grid_independence: str


class ImpactRequest(BaseModel):
    """Request for impact calculation."""
    simulation_data: SimulationResponse


class ImpactResponse(BaseModel):
    """Response with impact metrics."""
    metrics: ImpactMetrics


class ComparisonResponse(BaseModel):
    """Response comparing rule-based vs MILP."""
    rule_result: SimulationResponse
    milp_result: SimulationResponse
    cost_savings: float = Field(..., description="Cost difference (rule - milp)")
    improvement_percent: float = Field(..., description="Percentage improvement")
    different_decisions_count: int = Field(..., description="Number of hours with different decisions")
