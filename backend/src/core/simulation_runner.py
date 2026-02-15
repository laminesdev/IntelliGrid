"""
Simulation orchestrator for running energy scenarios.

Coordinates between:
- Environment simulator (generates solar/load/price data)
- Decision engine (policy-based actions)
- Battery model (physics)

Produces complete simulation results.
"""
from typing import List, Optional
from dataclasses import dataclass

from src.data.models import (
    SimulationConfig, SimulationResult, HourlyData, Action, EnvironmentState
)
from src.core.battery import Battery, BatteryState
from src.engine.decision_engine import DecisionEngine
from src.data.simulator import EnergyDataSimulator
from src.utils.config import GRID_EXPORT_PRICE


@dataclass
class StepResult:
    """Result of a single simulation step.
    
    Attributes:
        environment: Environment state for this hour
        action: Action taken
        battery_state: Battery state after action
        grid_import: Energy imported from grid (kWh)
        grid_export: Energy exported to grid (kWh)
        cost: Net cost for this hour (DZD)
    """
    environment: EnvironmentState
    action: Action
    battery_state: BatteryState
    grid_import: float
    grid_export: float
    cost: float


class SimulationRunner:
    """Orchestrates complete energy system simulation.
    
    Runs a 24-hour scenario by coordinating:
    1. Environment generation (solar, load, prices)
    2. Decision making (policy-based actions)
    3. Physics application (battery charge/discharge)
    4. Cost calculation
    
    This separation allows:
    - Testing different decision algorithms on same scenarios
    - Replaying scenarios with different parameters
    - Clean architecture without hidden coupling
    """
    
    def __init__(
        self,
        simulator: EnergyDataSimulator,
        decision_engine: DecisionEngine,
        battery: Battery
    ):
        """Initialize simulation runner.
        
        Args:
            simulator: Generates environment data (solar, load, prices)
            decision_engine: Makes policy decisions
            battery: Stateful battery model
        """
        self.simulator = simulator
        self.engine = decision_engine
        self.battery = battery
    
    def run(self, initial_soc: Optional[float] = None) -> SimulationResult:
        """Execute complete 24-hour simulation.
        
        Args:
            initial_soc: Starting SOC (0-1), uses battery's current if None
            
        Returns:
            SimulationResult with hourly data and aggregates
        """
        # Reset battery if initial_soc provided
        if initial_soc is not None:
            self.battery.reset(initial_soc)
        
        # Generate environment for 24 hours
        environments = self.simulator.generate_24h_environment()
        
        # Run simulation
        result = SimulationResult()
        result.seed = self.simulator.seed  # Store seed for reproducibility
        
        for env in environments:
            step_result = self._run_step(env)
            
            # Convert to HourlyData for backward compatibility
            hourly = self._to_hourly_data(step_result)
            result.hourly_data.append(hourly)
            
            # Accumulate totals
            result.total_solar += env.solar_kwh
            result.total_consumption += env.load_kwh
            result.total_grid_usage += step_result.grid_import
            result.total_grid_export += step_result.grid_export
            result.total_cost += step_result.cost
        
        # Calculate savings (requires baseline comparison)
        result.total_savings = self._calculate_savings(environments)
        
        return result
    
    def _run_step(self, env: EnvironmentState) -> StepResult:
        """Execute single timestep.
        
        Args:
            env: Environment state for this hour
            
        Returns:
            StepResult with action and outcomes
        """
        # 1. Make decision based on policy
        action = self.engine.decide(env, self.battery.state)
        
        # 2. Apply physics based on action
        grid_import, grid_export = self._apply_action(action, env)
        
        # 3. Calculate cost
        cost = (grid_import * env.price) - (grid_export * GRID_EXPORT_PRICE)
        
        return StepResult(
            environment=env,
            action=action,
            battery_state=self.battery.state,
            grid_import=grid_import,
            grid_export=grid_export,
            cost=cost
        )
    
    def _apply_action(
        self,
        action: Action,
        env: EnvironmentState
    ) -> tuple[float, float]:
        """Apply action and return grid import/export.
        
        Args:
            action: Action to apply
            env: Environment state
            
        Returns:
            Tuple of (grid_import, grid_export) in kWh
        """
        net = env.solar_kwh - env.load_kwh
        
        if action == Action.CHARGE_BATTERY:
            # Charge from solar surplus
            if net > 0:
                self.battery.charge(net)
            return 0.0, 0.0
        
        elif action == Action.DISCHARGE_BATTERY:
            # Discharge to meet deficit
            if net < 0:
                demand = abs(net)
                drawn, delivered = self.battery.discharge(demand)
                remaining = demand - delivered
                return remaining, 0.0  # Import what battery couldn't cover
            return 0.0, 0.0
        
        elif action == Action.SELL_TO_GRID:
            # Export solar surplus
            if net > 0:
                return 0.0, net
            return 0.0, 0.0
        
        elif action == Action.USE_GRID:
            # Import to meet deficit
            if net < 0:
                return abs(net), 0.0
            return 0.0, 0.0
        
        else:  # IDLE
            return 0.0, 0.0
    
    def _to_hourly_data(self, step: StepResult) -> HourlyData:
        """Convert StepResult to HourlyData for backward compatibility.
        
        Args:
            step: Step result
            
        Returns:
            HourlyData for dashboard
        """
        env = step.environment
        
        # Calculate baseline cost (no battery scenario)
        baseline_grid = max(0, env.load_kwh - env.solar_kwh)
        baseline_cost = baseline_grid * env.price
        
        # Savings = baseline - actual
        savings = baseline_cost - step.cost
        
        return HourlyData(
            hour=env.hour,
            solar_production=round(env.solar_kwh, 2),
            consumption=round(env.load_kwh, 2),
            battery_level=round(step.battery_state.charge_kwh, 2),
            battery_soc=round(step.battery_state.soc, 2),
            grid_usage=round(step.grid_import, 2),
            grid_export=round(step.grid_export, 2),
            net_energy=round(env.solar_kwh - env.load_kwh, 2),
            action=step.action,
            grid_price=env.price,
            cost=round(step.cost, 3),
            savings=round(savings, 3)
        )
    
    def _calculate_savings(self, environments: List[EnvironmentState]) -> float:
        """Calculate total savings vs no-battery baseline.
        
        Args:
            environments: List of environment states
            
        Returns:
            Total savings in DZD
        """
        # Baseline: all consumption not met by solar comes from grid
        baseline_cost = sum(
            max(0, env.load_kwh - env.solar_kwh) * env.price
            for env in environments
        )
        
        # Actual cost is accumulated during simulation
        # This is approximate - for exact savings, we'd need to store it
        return 0.0  # Will be calculated properly in results
