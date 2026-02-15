"""
MILP-based Decision Engine for optimal energy management.

Uses Mixed Integer Linear Programming to solve the battery optimization problem
over the full time horizon (24 hours) rather than greedy hour-by-hour decisions.

Mathematical Formulation:
-------------------------
Variables (for each time t):
    - battery_charge[t]: Battery charge level (kWh)
    - grid_import[t]: Energy imported from grid (kWh)
    - grid_export[t]: Energy exported to grid (kWh)
    - charge_rate[t]: Charging power (kW)
    - discharge_rate[t]: Discharging power (kW)

Objective:
    Minimize sum(grid_import[t] * price[t] - grid_export[t] * export_price)

Constraints:
    1. Energy balance: solar[t] + discharge + import = load[t] + charge + export
    2. Battery dynamics: charge[t+1] = charge[t] + efficiency * charge_rate - discharge_rate
    3. SOC bounds: min_soc * capacity <= charge[t] <= max_soc * capacity
    4. Power limits: 0 <= charge_rate <= max_charge, 0 <= discharge_rate <= max_discharge
    5. No simultaneous charge/discharge (complementarity)
"""
from typing import List, Optional
import pulp

from src.data.models import Action, EnvironmentState
from src.core.battery import BatteryState, Battery
from src.utils.config import GRID_EXPORT_PRICE


class MILPDecisionEngine:
    """MILP-based optimization engine for energy management.
    
    Solves the battery scheduling problem as a Mixed Integer Linear Program
    over a 24-hour horizon to minimize total electricity costs.
    
    Advantages over rule-based:
    - Global optimization (not greedy)
    - Handles time-coupled decisions (lookahead)
    - Respects all constraints simultaneously
    - Provably optimal (within solver tolerance)
    
    Attributes:
        solver_name: Which MILP solver to use ('PULP_CBC_CMD' default)
        time_limit_sec: Maximum solve time (None for unlimited)
        mip_gap: Optimality gap tolerance (1% default)
    """
    
    def __init__(
        self,
        solver_name: str = 'PULP_CBC_CMD',
        time_limit_sec: Optional[int] = None,
        mip_gap: float = 0.01
    ):
        """Initialize MILP engine.
        
        Args:
            solver_name: MILP solver to use
            time_limit_sec: Max solve time in seconds (None = unlimited)
            mip_gap: Optimality gap (0.01 = 1%)
        """
        self.solver_name = solver_name
        self.time_limit_sec = time_limit_sec
        self.mip_gap = mip_gap
    
    def optimize_schedule(
        self,
        environments: List[EnvironmentState],
        initial_battery: BatteryState
    ) -> List[Action]:
        """Generate optimal 24-hour action schedule.
        
        Solves MILP to determine best action for each hour considering
        the full time horizon and all constraints.
        
        Args:
            environments: List of 24 EnvironmentState (one per hour)
            initial_battery: Starting battery state
            
        Returns:
            List of 24 Actions (one per hour)
        """
        # Build and solve MILP
        model, variables = self._build_milp(environments, initial_battery)
        
        # Solve
        solver = pulp.getSolver(
            self.solver_name,
            timeLimit=self.time_limit_sec,
            mip=self.mip_gap,
            msg=False  # Quiet output
        )
        
        model.solve(solver)
        
        # Check solution status
        if pulp.LpStatus[model.status] != 'Optimal':
            import logging
            logging.warning(f"MILP status = {pulp.LpStatus[model.status]}")
        
        # Extract actions from solution
        actions = []
        for t in range(24):
            action = self._determine_action_from_solution(variables, t)
            actions.append(action)
        
        return actions
    
    def _build_milp(
        self,
        environments: List[EnvironmentState],
        initial_battery: BatteryState
    ) -> tuple:
        """Build the MILP model.
        
        Args:
            environments: 24 hours of environment data
            initial_battery: Starting battery state
            
        Returns:
            Tuple of (model, variables_dict)
        """
        # Create model
        model = pulp.LpProblem("BatteryOptimization", pulp.LpMinimize)
        
        # Time periods
        T = range(24)
        
        # Extract data
        solar = [env.solar_kwh for env in environments]
        load = [env.load_kwh for env in environments]
        price = [env.price for env in environments]
        
        # Battery parameters
        capacity = initial_battery.capacity_kwh
        initial_charge = initial_battery.charge_kwh
        min_soc = Battery.MIN_SOC
        max_soc = Battery.MAX_SOC
        charge_eff = Battery.CHARGE_EFFICIENCY
        discharge_eff = Battery.DISCHARGE_EFFICIENCY
        max_charge_rate = Battery.MAX_CHARGE_RATE_KW
        max_discharge_rate = Battery.MAX_DISCHARGE_RATE_KW
        export_price = GRID_EXPORT_PRICE  # DZD/kWh
        
        # Decision variables
        # Battery charge level at end of each period
        battery_charge = pulp.LpVariable.dicts(
            "battery_charge", T, 
            lowBound=min_soc * capacity, 
            upBound=max_soc * capacity
        )
        
        # Grid import (buying from grid)
        grid_import = pulp.LpVariable.dicts(
            "grid_import", T, lowBound=0
        )
        
        # Grid export (selling to grid)
        grid_export = pulp.LpVariable.dicts(
            "grid_export", T, lowBound=0
        )
        
        # Charging power from solar
        charge_rate = pulp.LpVariable.dicts(
            "charge_rate", T, lowBound=0, upBound=max_charge_rate
        )
        
        # Discharging power to meet load
        discharge_rate = pulp.LpVariable.dicts(
            "discharge_rate", T, lowBound=0, upBound=max_discharge_rate
        )
        
        # Binary variable: 1 if charging, 0 if discharging (prevents simultaneous)
        is_charging = pulp.LpVariable.dicts(
            "is_charging", T, cat='Binary'
        )
        
        # Objective: Minimize total cost
        # Cost = import * price - export * export_price
        model += pulp.lpSum([
            grid_import[t] * price[t] - grid_export[t] * export_price
            for t in T
        ])
        
        # Constraints
        for t in T:
            # Energy balance: solar + discharge + import = load + charge + export
            model += (
                solar[t] + discharge_rate[t] * discharge_eff + grid_import[t] ==
                load[t] + charge_rate[t] + grid_export[t],
                f"EnergyBalance_{t}"
            )
            
            # Battery dynamics
            if t == 0:
                # Initial condition
                model += (
                    battery_charge[t] == initial_charge + 
                    charge_rate[t] * charge_eff - discharge_rate[t],
                    f"BatteryDynamics_{t}"
                )
            else:
                # State transition
                model += (
                    battery_charge[t] == battery_charge[t-1] + 
                    charge_rate[t] * charge_eff - discharge_rate[t],
                    f"BatteryDynamics_{t}"
                )
            
            # Complementarity: Cannot charge and discharge simultaneously
            # If is_charging[t] = 1, then discharge_rate[t] = 0
            # If is_charging[t] = 0, then charge_rate[t] = 0
            M = max(max_charge_rate, max_discharge_rate)  # Big M
            
            model += (
                charge_rate[t] <= is_charging[t] * M,
                f"ChargeOnlyIfCharging_{t}"
            )
            model += (
                discharge_rate[t] <= (1 - is_charging[t]) * M,
                f"DischargeOnlyIfNotCharging_{t}"
            )
        
        return model, {
            'battery_charge': battery_charge,
            'grid_import': grid_import,
            'grid_export': grid_export,
            'charge_rate': charge_rate,
            'discharge_rate': discharge_rate,
            'is_charging': is_charging
        }
    
    def _determine_action_from_solution(self, variables: dict, t: int) -> Action:
        """Determine discrete action from MILP solution.
        
        Args:
            variables: MILP variables dict
            t: Time period
            
        Returns:
            Action enum
        """
        charge_rate = pulp.value(variables['charge_rate'][t])
        discharge_rate = pulp.value(variables['discharge_rate'][t])
        grid_export = pulp.value(variables['grid_export'][t])
        
        # Determine action based on solution
        if charge_rate > 0.01:  # Charging
            return Action.CHARGE_BATTERY
        elif discharge_rate > 0.01:  # Discharging
            return Action.DISCHARGE_BATTERY
        elif grid_export > 0.01:  # Exporting
            return Action.SELL_TO_GRID
        else:
            # Check if importing
            grid_import = pulp.value(variables['grid_import'][t])
            if grid_import > 0.01:
                return Action.USE_GRID
            else:
                return Action.IDLE
    
    def get_schedule_details(
        self,
        environments: List[EnvironmentState],
        initial_battery: BatteryState
    ) -> List[dict]:
        """Get detailed schedule with all variable values.
        
        Useful for debugging and visualization.
        
        Args:
            environments: 24 hours of environment data
            initial_battery: Starting battery state
            
        Returns:
            List of dicts with detailed solution for each hour
        """
        model, variables = self._build_milp(environments, initial_battery)
        
        solver = pulp.getSolver(
            self.solver_name,
            timeLimit=self.time_limit_sec,
            mip=self.mip_gap,
            msg=False
        )
        
        model.solve(solver)
        
        details = []
        for t in range(24):
            details.append({
                'hour': t,
                'battery_charge': pulp.value(variables['battery_charge'][t]),
                'grid_import': pulp.value(variables['grid_import'][t]),
                'grid_export': pulp.value(variables['grid_export'][t]),
                'charge_rate': pulp.value(variables['charge_rate'][t]),
                'discharge_rate': pulp.value(variables['discharge_rate'][t]),
                'action': self._determine_action_from_solution(variables, t)
            })
        
        return details
