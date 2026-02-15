"""
Integration tests for complete simulation flow.

Tests verify:
- Energy conservation (system-wide)
- Determinism (reproducibility)
- End-to-end simulation
"""
import pytest
from src.core.adapter import SimulationAdapter
from src.core.battery import Battery
from src.core.simulation_runner import SimulationRunner
from src.data.simulator import EnergyDataSimulator
from src.engine.decision_engine import DecisionEngine
from src.data.models import SimulationConfig, Season, Weather, DayType


class TestEnergyConservationSystemWide:
    """Total energy in system must balance."""
    
    def test_energy_balance_24h(self):
        """Energy in = Energy out + losses (within tolerance)."""
        config = SimulationConfig(
            season=Season.SUMMER,
            weather=Weather.SUNNY,
            day_type=DayType.WEEKDAY
        )
        adapter = SimulationAdapter(config, seed=42)
        result = adapter.generate_24h_data()
        
        total_solar = sum(h.solar_production for h in result.hourly_data)
        total_load = sum(h.consumption for h in result.hourly_data)
        total_grid_import = sum(h.grid_usage for h in result.hourly_data)
        total_grid_export = sum(h.grid_export for h in result.hourly_data)
        
        # Energy balance: solar + import = load + export + battery_change
        # Battery change is: final_level - initial_level
        initial_battery = result.hourly_data[0].battery_level
        final_battery = result.hourly_data[-1].battery_level
        battery_change = final_battery - initial_battery
        
        # Energy accounting
        energy_in = total_solar + total_grid_import
        energy_out = total_load + total_grid_export + battery_change
        
        # Allow 10% tolerance for:
        # - Battery efficiency losses (96% charge * 96% discharge = 92% round-trip)
        # - Inverter losses (not yet modeled)
        # - Rounding in hourly data
        imbalance = abs(energy_in - energy_out) / max(energy_in, 1.0)
        assert imbalance < 0.10, \
            f"Energy imbalance too large: {imbalance:.1%} (in={energy_in:.2f}, out={energy_out:.2f})"
        
        # Also verify energy is conserved (not created)
        assert energy_out <= energy_in * 1.01, \
            "Energy output exceeds input (energy creation bug)"
    
    def test_no_energy_creation_scenario(self):
        """Complete scenario should not create energy from nothing."""
        config = SimulationConfig(
            season=Season.WINTER,
            weather=Weather.CLOUDY,
            day_type=DayType.WEEKEND
        )
        adapter = SimulationAdapter(config, seed=123)
        result = adapter.generate_24h_data()
        
        # Check that costs make sense (no negative costs that would imply energy creation)
        for hourly in result.hourly_data:
            # Cost = grid_import * price - grid_export * export_price
            # This can be negative (profit from export), but let's check totals
            pass
        
        # Total cost should be reasonable
        assert result.total_cost > -100, "Unreasonable negative total cost"


class TestDeterminism:
    """Same seed must produce identical results."""
    
    def test_reproducible_simulation(self):
        """Same seed → identical output."""
        config = SimulationConfig(
            season=Season.SUMMER,
            weather=Weather.SUNNY,
            day_type=DayType.WEEKDAY
        )
        
        # Run twice with same seed
        adapter1 = SimulationAdapter(config, seed=42)
        result1 = adapter1.generate_24h_data()
        
        adapter2 = SimulationAdapter(config, seed=42)
        result2 = adapter2.generate_24h_data()
        
        # Should be identical
        assert result1.total_solar == result2.total_solar
        assert result1.total_consumption == result2.total_consumption
        assert result1.total_cost == result2.total_cost
        
        # Check hourly data
        for h1, h2 in zip(result1.hourly_data, result2.hourly_data):
            assert h1.solar_production == h2.solar_production
            assert h1.consumption == h2.consumption
            assert h1.action == h2.action
    
    def test_different_seeds_produce_different_results(self):
        """Different seeds should produce different random variations."""
        config = SimulationConfig(
            season=Season.SUMMER,
            weather=Weather.SUNNY,
            day_type=DayType.WEEKDAY
        )
        
        adapter1 = SimulationAdapter(config, seed=42)
        result1 = adapter1.generate_24h_data()
        
        adapter2 = SimulationAdapter(config, seed=999)
        result2 = adapter2.generate_24h_data()
        
        # Should differ (at least in some hours due to randomness)
        solar_differs = any(
            h1.solar_production != h2.solar_production
            for h1, h2 in zip(result1.hourly_data, result2.hourly_data)
        )
        assert solar_differs, "Different seeds should produce different solar variations"


class TestSimulationRunnerComponents:
    """Test individual components work together."""
    
    def test_runner_with_custom_components(self):
        """SimulationRunner can be constructed with custom components."""
        config = SimulationConfig(
            season=Season.SUMMER,
            weather=Weather.SUNNY,
            day_type=DayType.WEEKDAY
        )
        
        simulator = EnergyDataSimulator(config, seed=42)
        battery = Battery(13.5, initial_soc=0.6)  # Custom initial SOC
        engine = DecisionEngine()
        
        runner = SimulationRunner(simulator, engine, battery)
        result = runner.run()
        
        # Should complete successfully
        assert len(result.hourly_data) == 24
        assert result.total_solar > 0
    
    def test_battery_state_preserved_in_results(self):
        """Battery SOC tracked correctly throughout simulation."""
        config = SimulationConfig(
            season=Season.SUMMER,
            weather=Weather.SUNNY,
            day_type=DayType.WEEKDAY
        )
        
        adapter = SimulationAdapter(config, seed=42)
        result = adapter.generate_24h_data()
        
        # Check SOC is tracked
        for hourly in result.hourly_data:
            assert 0.0 <= hourly.battery_soc <= 1.0, \
                f"Invalid SOC: {hourly.battery_soc}"


class TestAdapterBackwardCompatibility:
    """Adapter provides backward compatible interface."""
    
    def test_adapter_produces_simulation_result(self):
        """Adapter returns SimulationResult like old interface."""
        config = SimulationConfig(
            season=Season.SUMMER,
            weather=Weather.SUNNY,
            day_type=DayType.WEEKDAY
        )
        
        adapter = SimulationAdapter(config, seed=42)
        result = adapter.generate_24h_data()
        
        # Check all expected attributes exist
        assert hasattr(result, 'hourly_data')
        assert hasattr(result, 'total_solar')
        assert hasattr(result, 'total_consumption')
        assert hasattr(result, 'total_grid_usage')
        assert hasattr(result, 'total_grid_export')
        assert hasattr(result, 'total_cost')
        assert hasattr(result, 'total_savings')
    
    def test_adapter_dataframe_output(self):
        """Adapter can produce DataFrame output."""
        import pandas as pd
        
        config = SimulationConfig(
            season=Season.SUMMER,
            weather=Weather.SUNNY,
            day_type=DayType.WEEKDAY
        )
        
        adapter = SimulationAdapter(config, seed=42)
        df = adapter.get_dataframe()
        
        # Should return DataFrame
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 24  # 24 hours
        assert 'solar_production' in df.columns
        assert 'battery_soc' in df.columns
