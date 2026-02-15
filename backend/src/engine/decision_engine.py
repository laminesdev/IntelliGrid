"""
Decision Engine for intelligent energy management.

Implements policy-based decision making that determines WHAT action to take,
leaving the physics (HOW MUCH) to the Battery class.

Policy:
- Solar surplus + battery not full → Charge battery
- Solar surplus + battery full → Sell to grid
- Solar deficit + peak hours + battery available → Discharge battery
- Solar deficit + battery available → Discharge battery
- Solar deficit + battery low → Use grid
"""
from src.data.models import Action, EnvironmentState
from src.core.battery import BatteryState


class DecisionEngine:
    """Policy-based decision engine for energy optimization.
    
    This engine decides WHAT action to take based on:
    - Current environment (solar, load, price)
    - Battery state (SOC, capacity)
    - Time-of-Use pricing signals
    
    It does NOT calculate energy amounts - that's handled by the Battery class.
    
    Attributes:
        peak_hours: Hours considered peak pricing (18:00-22:00)
        night_hours: Hours considered night pricing (23:00-07:00)
        peak_soc_threshold: Minimum SOC to discharge during peak (0.40)
        min_soc_threshold: Absolute minimum SOC to discharge (0.20)
        max_soc_threshold: SOC above which to stop charging (0.95)
    """
    
    def __init__(self):
        """Initialize decision engine with policy parameters."""
        self.peak_hours = list(range(18, 22))  # 18:00-22:00
        self.night_hours = list(range(23, 24)) + list(range(0, 7))  # 23:00-07:00
        self.peak_soc_threshold = 0.40
        self.min_soc_threshold = 0.20
        self.max_soc_threshold = 0.95
    
    def decide(
        self,
        env: EnvironmentState,
        battery: BatteryState
    ) -> Action:
        """Determine the optimal action for current conditions.
        
        Args:
            env: Current environment state (solar, load, price, hour)
            battery: Current battery state (SOC, charge level)
            
        Returns:
            Action enum indicating what to do:
            - CHARGE_BATTERY: Store excess solar in battery
            - DISCHARGE_BATTERY: Use battery to meet load
            - SELL_TO_GRID: Export excess solar to grid
            - USE_GRID: Import from grid to meet load
            - IDLE: No action needed
        """
        net_energy = env.solar_kwh - env.load_kwh
        
        if net_energy >= 0:
            # Solar surplus - either charge or export
            return self._handle_surplus(net_energy, battery)
        else:
            # Solar deficit - either discharge or import
            return self._handle_deficit(abs(net_energy), battery, env.hour, env.price)
    
    def _handle_surplus(
        self,
        surplus: float,
        battery: BatteryState
    ) -> Action:
        """Determine action when solar exceeds load.
        
        Policy:
        1. If battery has room, charge it
        2. Otherwise, export to grid
        
        Args:
            surplus: Excess solar energy (kWh)
            battery: Current battery state
            
        Returns:
            Action.CHARGE_BATTERY or Action.SELL_TO_GRID
        """
        if battery.soc < self.max_soc_threshold:
            return Action.CHARGE_BATTERY
        else:
            return Action.SELL_TO_GRID
    
    def _handle_deficit(
        self,
        deficit: float,
        battery: BatteryState,
        hour: int,
        price: float
    ) -> Action:
        """Determine action when load exceeds solar.
        
        Policy:
        1. Peak hours + sufficient battery → Discharge aggressively
        2. Any hour + battery above minimum → Discharge normally
        3. Battery too low → Import from grid
        
        Args:
            deficit: Energy shortage (kWh)
            battery: Current battery state
            hour: Current hour (for TOU pricing)
            price: Current grid price (DZD/kWh)
            
        Returns:
            Action.DISCHARGE_BATTERY or Action.USE_GRID
        """
        is_peak = hour in self.peak_hours
        
        # Peak hours: Use battery aggressively to avoid peak prices
        if is_peak and battery.soc > self.peak_soc_threshold:
            return Action.DISCHARGE_BATTERY
        
        # Normal hours: Use battery if above minimum
        if battery.soc > self.min_soc_threshold:
            return Action.DISCHARGE_BATTERY
        
        # Battery too low - must use grid
        return Action.USE_GRID
    
    def should_conserve_energy(
        self,
        current_hour: int,
        battery: BatteryState,
        tomorrow_cloudy: bool
    ) -> bool:
        """Determine if system should enter conservation mode.
        
        Conservation mode recommended when:
        - Late evening + low battery + cloudy forecast tomorrow
        - Battery at critical level (< 15%)
        
        Args:
            current_hour: Current hour (0-23)
            battery: Current battery state
            tomorrow_cloudy: True if cloudy weather forecasted
            
        Returns:
            True if conservation mode recommended
        """
        # Late evening + low battery + cloudy tomorrow = conserve
        if current_hour >= 20 and battery.soc < 0.30 and tomorrow_cloudy:
            return True
        
        # Critical battery level
        if battery.soc < 0.15:
            return True
        
        return False
