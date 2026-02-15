"""
Hybrid Simulation Adapter supporting both rule-based and MILP optimization.

Allows easy comparison between rule-based and MILP approaches.
"""
from typing import Optional, Literal
import pandas as pd

from src.data.models import SimulationConfig, SimulationResult
from src.data.simulator import EnergyDataSimulator
from src.engine.decision_engine import DecisionEngine
from src.engine.milp_engine import MILPDecisionEngine
from src.core.battery import Battery
from src.core.simulation_runner import SimulationRunner


class HybridSimulationAdapter:
    """Adapter supporting both rule-based and MILP optimization.
    
    Provides unified interface to run simulations with either:
    - Rule-based: Fast, greedy decisions (original approach)
    - MILP: Optimal, lookahead-based decisions (Phase C)
    
    Usage:
        adapter = HybridSimulationAdapter(config, seed=42, mode='milp')
        result = adapter.generate_24h_data()
    
    Attributes:
        config: Simulation configuration
        seed: Random seed for reproducibility
        mode: 'rule' or 'milp'
    """
    
    def __init__(
        self,
        config: SimulationConfig,
        seed: Optional[int] = None,
        mode: Literal['rule', 'milp'] = 'rule'
    ):
        """Initialize adapter.
        
        Args:
            config: Simulation configuration
            seed: Random seed for reproducibility
            mode: 'rule' for rule-based, 'milp' for optimization
        """
        self.config = config
        self.seed = seed
        self.mode = mode
        
        # Create simulator (same for both modes)
        self._simulator = EnergyDataSimulator(config, seed)
        
        # Create battery (same for both modes)
        self._battery = Battery(13.5, initial_soc=0.5)
        
        # Create appropriate engine
        if mode == 'rule':
            self._engine = DecisionEngine()
        else:  # milp
            self._engine = MILPDecisionEngine()
        
        # Create runner (only works with rule-based engine directly)
        if mode == 'rule':
            self._runner = SimulationRunner(
                self._simulator,
                self._engine,
                self._battery
            )
    
    def generate_24h_data(self) -> SimulationResult:
        """Generate complete 24-hour simulation.
        
        Returns:
            SimulationResult with hourly data
        """
        if self.mode == 'rule':
            # Use standard runner
            return self._runner.run()
        else:  # milp
            # MILP needs full horizon upfront
            return self._run_milp_simulation()
    
    def _run_milp_simulation(self) -> SimulationResult:
        """Run simulation using MILP optimization.
        
        MILP optimizes the full 24-hour schedule at once, then
        we apply it hour by hour with the battery physics.
        
        Returns:
            SimulationResult
        """
        from src.data.models import HourlyData
        from src.utils.config import GRID_EXPORT_PRICE
        
        # Generate environment for all 24 hours
        environments = self._simulator.generate_24h_environment()
        
        # Get optimal schedule from MILP
        initial_battery = self._battery.state
        actions = self._engine.optimize_schedule(environments, initial_battery)
        
        # Execute schedule with physics
        result = SimulationResult()
        result.seed = self.seed
        
        for t, (env, action) in enumerate(zip(environments, actions)):
            # Apply action
            grid_import, grid_export = self._apply_action(action, env)
            
            # Calculate cost
            cost = (grid_import * env.price) - (grid_export * GRID_EXPORT_PRICE)
            
            # Calculate baseline cost (no battery)
            baseline_grid = max(0, env.load_kwh - env.solar_kwh)
            baseline_cost = baseline_grid * env.price
            savings = baseline_cost - cost
            
            # Create hourly data
            hourly = HourlyData(
                hour=env.hour,
                solar_production=round(env.solar_kwh, 2),
                consumption=round(env.load_kwh, 2),
                battery_level=round(self._battery.state.charge_kwh, 2),
                battery_soc=round(self._battery.state.soc, 2),
                grid_usage=round(grid_import, 2),
                grid_export=round(grid_export, 2),
                net_energy=round(env.solar_kwh - env.load_kwh, 2),
                action=action,
                grid_price=env.price,
                cost=round(cost, 3),
                savings=round(savings, 3)
            )
            
            result.hourly_data.append(hourly)
            result.total_solar += env.solar_kwh
            result.total_consumption += env.load_kwh
            result.total_grid_usage += grid_import
            result.total_grid_export += grid_export
            result.total_cost += cost
            result.total_savings += savings
        
        return result
    
    def _apply_action(self, action, env):
        """Apply action and return grid import/export."""
        net = env.solar_kwh - env.load_kwh
        
        if action.value == 'charge_battery':
            if net > 0:
                self._battery.charge(net)
            return 0.0, 0.0
        elif action.value == 'discharge_battery':
            if net < 0:
                demand = abs(net)
                drawn, delivered = self._battery.discharge(demand)
                remaining = demand - delivered
                return remaining, 0.0
            return 0.0, 0.0
        elif action.value == 'sell_to_grid':
            if net > 0:
                return 0.0, net
            return 0.0, 0.0
        elif action.value == 'use_grid':
            if net < 0:
                return abs(net), 0.0
            return 0.0, 0.0
        else:
            return 0.0, 0.0
    
    def get_dataframe(self) -> pd.DataFrame:
        """Get simulation results as DataFrame."""
        result = self.generate_24h_data()
        return pd.DataFrame(result.to_dict())
    
    def compare_modes(self) -> dict:
        """Compare rule-based vs MILP performance.
        
        Returns:
            Dict with comparison metrics
        """
        # Run rule-based
        self.mode = 'rule'
        self._battery.reset(0.5)  # Reset battery
        rule_result = self.generate_24h_data()
        
        # Run MILP
        self.mode = 'milp'
        self._battery.reset(0.5)  # Reset battery
        milp_result = self.generate_24h_data()
        
        return {
            'rule_cost': rule_result.total_cost,
            'milp_cost': milp_result.total_cost,
            'savings': rule_result.total_cost - milp_result.total_cost,
            'improvement_pct': (
                (rule_result.total_cost - milp_result.total_cost) / 
                abs(rule_result.total_cost) * 100
            ) if rule_result.total_cost != 0 else 0,
            'rule_grid_import': rule_result.total_grid_usage,
            'milp_grid_import': milp_result.total_grid_usage,
        }
