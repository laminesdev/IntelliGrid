"""
Adapter for backward compatibility with existing dashboard.

Provides old interface while using new clean architecture internally.
This allows gradual migration without breaking the UI.
"""
from typing import Optional
import pandas as pd

from src.data.models import SimulationConfig, SimulationResult
from src.data.simulator import EnergyDataSimulator
from src.engine.decision_engine import DecisionEngine
from src.core.battery import Battery
from src.core.simulation_runner import SimulationRunner


class SimulationAdapter:
    """Adapter that provides old EnergyDataSimulator interface.
    
    Wraps the new SimulationRunner to maintain backward compatibility
    with the existing dashboard code.
    
    Old interface:
        simulator = EnergyDataSimulator(config)
        result = simulator.generate_24h_data()
    
    New internal:
        simulator = EnergyDataSimulator(config, seed)
        battery = Battery(...)
        engine = DecisionEngine()
        runner = SimulationRunner(simulator, engine, battery)
        result = runner.run()
    
    Attributes:
        config: Simulation configuration
        seed: Random seed for reproducibility
        _runner: Internal SimulationRunner instance
    """
    
    def __init__(self, config: SimulationConfig, seed: Optional[int] = None):
        """Initialize adapter.
        
        Args:
            config: Simulation configuration
            seed: Random seed for reproducible results
        """
        self.config = config
        self.seed = seed
        
        # Create new architecture components
        self._simulator = EnergyDataSimulator(config, seed)
        self._battery = Battery(13.5, initial_soc=0.5)
        self._engine = DecisionEngine()
        self._runner = SimulationRunner(
            self._simulator,
            self._engine,
            self._battery
        )
    
    def generate_24h_data(self) -> SimulationResult:
        """Generate complete 24-hour simulation (old interface).
        
        Returns:
            SimulationResult compatible with existing dashboard
        """
        return self._runner.run()
    
    def get_dataframe(self) -> pd.DataFrame:
        """Get simulation results as DataFrame (old interface).
        
        Returns:
            DataFrame with hourly data
        """
        result = self.generate_24h_data()
        return pd.DataFrame(result.to_dict())
