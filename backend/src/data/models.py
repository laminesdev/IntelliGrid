"""
Data models and classes for IntelliGrid.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class Season(Enum):
    SUMMER = "summer"
    WINTER = "winter"


class Weather(Enum):
    SUNNY = "sunny"
    PARTLY_CLOUDY = "partly_cloudy"
    CLOUDY = "cloudy"
    RAINY = "rainy"


class DayType(Enum):
    WEEKDAY = "weekday"
    WEEKEND = "weekend"


class Action(Enum):
    CHARGE_BATTERY = "charge_battery"
    DISCHARGE_BATTERY = "discharge_battery"
    SELL_TO_GRID = "sell_to_grid"
    USE_GRID = "use_grid"
    IDLE = "idle"


@dataclass
class BatteryState:
    """Represents the current state of the home battery system."""
    current_charge: float  # Current charge in kWh
    max_capacity: float = 13.5  # Maximum capacity in kWh
    charge_rate: float = 5.0  # Max charge rate in kW
    discharge_rate: float = 5.0  # Max discharge rate in kW
    efficiency: float = 0.92  # Round-trip efficiency
    
    @property
    def state_of_charge(self) -> float:
        """Return battery state of charge as percentage (0-1)."""
        return self.current_charge / self.max_capacity
    
    @property
    def available_capacity(self) -> float:
        """Return available capacity for charging in kWh."""
        return self.max_capacity - self.current_charge
    
    @property
    def available_discharge(self) -> float:
        """Return available energy for discharge in kWh."""
        return self.current_charge


@dataclass
class SimulationConfig:
    """Configuration for energy simulation."""
    season: Season
    weather: Weather
    day_type: DayType
    tomorrow_weather: Optional[Weather] = None
    hours: int = 24


@dataclass
class HourlyData:
    """Data for a single hour of simulation."""
    hour: int
    solar_production: float  # kWh
    consumption: float  # kWh
    battery_level: float  # kWh
    battery_soc: float  # State of charge (0-1)
    grid_usage: float  # kWh imported from grid
    grid_export: float  # kWh exported to grid
    net_energy: float  # Solar - Consumption
    action: Action
    grid_price: float  # DZD/kWh
    cost: float  # Cost for this hour
    savings: float  # Savings vs baseline


@dataclass
class SimulationResult:
    """Complete results of a 24-hour simulation."""
    hourly_data: List[HourlyData] = field(default_factory=list)
    total_solar: float = 0.0
    total_consumption: float = 0.0
    total_grid_usage: float = 0.0
    total_grid_export: float = 0.0
    total_cost: float = 0.0
    total_savings: float = 0.0
    seed: Optional[int] = None
    
    def to_dict(self) -> Dict:
        """Convert result to dictionary format."""
        return {
            "hour": [d.hour for d in self.hourly_data],
            "solar_production": [d.solar_production for d in self.hourly_data],
            "consumption": [d.consumption for d in self.hourly_data],
            "battery_level": [d.battery_level for d in self.hourly_data],
            "battery_soc": [d.battery_soc for d in self.hourly_data],
            "grid_usage": [d.grid_usage for d in self.hourly_data],
            "grid_export": [d.grid_export for d in self.hourly_data],
            "net_energy": [d.net_energy for d in self.hourly_data],
            "action": [d.action.value for d in self.hourly_data],
            "grid_price": [d.grid_price for d in self.hourly_data],
            "cost": [d.cost for d in self.hourly_data],
            "savings": [d.savings for d in self.hourly_data],
        }


@dataclass
class Alert:
    """Weather or system alert."""
    type: str  # "warning", "info", "success", "danger"
    message: str
    priority: int  # 1 (highest) to 5 (lowest)
    recommendation: str
    icon: str = "ℹ️"


@dataclass
class ImpactMetrics:
    """Environmental and financial impact metrics."""
    # Waste metrics
    wasted_without_system: float  # kWh
    wasted_with_system: float  # kWh
    waste_reduction_percent: float
    
    # Financial metrics
    daily_cost_without_battery: float
    daily_cost_with_battery: float
    daily_savings: float
    yearly_savings: float
    ten_year_savings: float
    roi_percent: float
    payback_years: float
    export_revenue_daily: float
    export_revenue_yearly: float
    
    # Environmental metrics
    co2_reduced_tons: float
    trees_equivalent: float
    energy_saved_kwh: float
    
    # Enhanced environmental metrics
    water_saved_liters: float  # Liters of water saved per year
    nox_reduced_kg: float  # kg NOx reduced per year
    so2_reduced_kg: float  # kg SO2 reduced per year
    pm10_reduced_kg: float  # kg PM10 reduced per year
    
    # Transport equivalence
    car_km_equivalent: float  # km driven by average car
    bus_km_equivalent: float  # km driven by bus
    
    # Energy independence
    grid_independence_percent: float  # % reduction in grid dependency


@dataclass(frozen=True)
class EnvironmentState:
    """Environment state for a single timestep.
    
    Immutable snapshot of solar, load, and pricing conditions.
    
    Attributes:
        hour: Hour of day (0-23)
        solar_kwh: Solar production in kWh
        load_kwh: Energy consumption in kWh
        price: Grid price in DZD/kWh
    """
    hour: int
    solar_kwh: float
    load_kwh: float
    price: float