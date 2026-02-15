"""
Core battery physics module.

Implements stateful battery model with separate charge/discharge efficiencies.
"""
from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class BatteryState:
    """Immutable battery state snapshot.
    
    Attributes:
        charge_kwh: Current charge in kWh
        capacity_kwh: Maximum capacity in kWh
        soc: State of charge (0.0 to 1.0)
    """
    charge_kwh: float
    capacity_kwh: float
    soc: float


class Battery:
    """Stateful battery with realistic physics.
    
    Models battery behavior with:
    - Separate charge and discharge efficiencies
    - SOC constraints (min/max)
    - Power rate limits
    - Temperature-independent (for now)
    
    Attributes:
        CHARGE_EFFICIENCY: Efficiency when charging (0.96 = 96%)
        DISCHARGE_EFFICIENCY: Efficiency when discharging (0.96 = 96%)
        MIN_SOC: Minimum state of charge (0.20 = 20%)
        MAX_SOC: Maximum state of charge (0.95 = 95%)
        MAX_CHARGE_RATE_KW: Maximum charge power in kW
        MAX_DISCHARGE_RATE_KW: Maximum discharge power in kW
    """
    
    CHARGE_EFFICIENCY = 0.96
    DISCHARGE_EFFICIENCY = 0.96
    MIN_SOC = 0.20
    MAX_SOC = 0.95
    MAX_CHARGE_RATE_KW = 5.0
    MAX_DISCHARGE_RATE_KW = 5.0
    
    def __init__(self, capacity_kwh: float, initial_soc: float = 0.5):
        """Initialize battery.
        
        Args:
            capacity_kwh: Maximum capacity in kWh
            initial_soc: Initial state of charge (0.0 to 1.0)
        """
        if capacity_kwh <= 0:
            raise ValueError("Capacity must be positive")
        if not 0.0 <= initial_soc <= 1.0:
            raise ValueError("Initial SOC must be between 0 and 1")
            
        self.capacity_kwh = capacity_kwh
        self.charge_kwh = capacity_kwh * initial_soc
    
    @property
    def state(self) -> BatteryState:
        """Get current battery state.
        
        Returns:
            BatteryState with current values
        """
        return BatteryState(
            charge_kwh=self.charge_kwh,
            capacity_kwh=self.capacity_kwh,
            soc=self.charge_kwh / self.capacity_kwh
        )
    
    def charge(self, available_kwh: float) -> Tuple[float, float]:
        """Attempt to charge battery from available energy.
        
        Physics:
        - Energy stored = energy_converted * CHARGE_EFFICIENCY
        - Cannot exceed MAX_SOC
        - Cannot exceed MAX_CHARGE_RATE_KW
        
        Args:
            available_kwh: Energy available for charging in kWh
            
        Returns:
            Tuple of (energy_consumed, energy_stored) in kWh
        """
        if available_kwh <= 0:
            return 0.0, 0.0
        
        # Calculate maximum energy we can convert to stay under MAX_SOC
        max_storable = (self.MAX_SOC * self.capacity_kwh) - self.charge_kwh
        max_convertible = max_storable / self.CHARGE_EFFICIENCY
        
        # Limit by available energy, max rate, and max convertible
        energy_to_convert = min(
            available_kwh,
            max_convertible,
            self.MAX_CHARGE_RATE_KW
        )
        
        # Apply efficiency
        energy_stored = energy_to_convert * self.CHARGE_EFFICIENCY
        
        # Update state
        self.charge_kwh += energy_stored
        
        return energy_to_convert, energy_stored
    
    def discharge(self, demand_kwh: float) -> Tuple[float, float]:
        """Attempt to discharge battery to meet demand.
        
        Physics:
        - Energy delivered = energy_drawn * DISCHARGE_EFFICIENCY
        - Cannot go below MIN_SOC
        - Cannot exceed MAX_DISCHARGE_RATE_KW
        
        Args:
            demand_kwh: Energy demand in kWh
            
        Returns:
            Tuple of (energy_drawn, energy_delivered) in kWh
        """
        if demand_kwh <= 0:
            return 0.0, 0.0
        
        # Calculate maximum energy we can draw while staying above MIN_SOC
        max_drawable = self.charge_kwh - (self.MIN_SOC * self.capacity_kwh)
        
        # To deliver 'demand_kwh', we need to draw more (accounting for efficiency)
        energy_needed = demand_kwh / self.DISCHARGE_EFFICIENCY
        
        # Limit by demand, max rate, and max drawable
        energy_to_draw = min(
            energy_needed,
            max_drawable,
            self.MAX_DISCHARGE_RATE_KW
        )
        
        # Apply efficiency
        energy_delivered = energy_to_draw * self.DISCHARGE_EFFICIENCY
        
        # Update state
        self.charge_kwh -= energy_to_draw
        
        return energy_to_draw, energy_delivered
    
    def reset(self, soc: float = 0.5) -> None:
        """Reset battery to initial state.
        
        Args:
            soc: State of charge to reset to (0.0 to 1.0)
        """
        if not 0.0 <= soc <= 1.0:
            raise ValueError("SOC must be between 0 and 1")
        self.charge_kwh = self.capacity_kwh * soc
