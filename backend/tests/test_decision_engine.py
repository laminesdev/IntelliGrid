"""
Unit tests for DecisionEngine.

Tests policy decisions without physics.
"""
import pytest
from src.engine.decision_engine import DecisionEngine
from src.data.models import Action, EnvironmentState
from src.core.battery import Battery, BatteryState


class TestSurplusScenarios:
    """When solar production exceeds consumption."""
    
    def test_solar_surplus_with_room_charges_battery(self):
        """Excess solar should charge battery when SOC < max."""
        engine = DecisionEngine()
        env = EnvironmentState(hour=12, solar_kwh=10.0, load_kwh=3.0, price=0.18)
        battery = Battery(13.5, initial_soc=0.5).state
        
        action = engine.decide(env, battery)
        
        assert action == Action.CHARGE_BATTERY
    
    def test_solar_surplus_full_battery_exports_to_grid(self):
        """Excess solar should export when battery is full."""
        engine = DecisionEngine()
        env = EnvironmentState(hour=12, solar_kwh=10.0, load_kwh=3.0, price=0.18)
        battery = Battery(13.5, initial_soc=0.96).state  # Above max threshold
        
        action = engine.decide(env, battery)
        
        assert action == Action.SELL_TO_GRID
    
    def test_solar_surplus_exact_match_charges(self):
        """Even tiny surplus should attempt to charge if room available."""
        engine = DecisionEngine()
        env = EnvironmentState(hour=12, solar_kwh=5.1, load_kwh=5.0, price=0.18)
        battery = Battery(13.5, initial_soc=0.5).state
        
        action = engine.decide(env, battery)
        
        assert action == Action.CHARGE_BATTERY


class TestDeficitScenarios:
    """When consumption exceeds solar production."""
    
    def test_peak_hours_discharge_if_sufficient_battery(self):
        """During peak, discharge if SOC > 40%."""
        engine = DecisionEngine()
        
        for peak_hour in [18, 19, 20, 21]:
            env = EnvironmentState(
                hour=peak_hour, solar_kwh=2.0, load_kwh=8.0, price=0.30
            )
            battery = Battery(13.5, initial_soc=0.5).state  # 50% > 40%
            
            action = engine.decide(env, battery)
            
            assert action == Action.DISCHARGE_BATTERY, \
                f"Should discharge during peak hour {peak_hour} with 50% SOC"
    
    def test_peak_hours_discharge_if_above_minimum(self):
        """During peak, discharge if above absolute minimum (20%), even if below peak threshold (40%)."""
        engine = DecisionEngine()
        env = EnvironmentState(hour=19, solar_kwh=2.0, load_kwh=8.0, price=0.30)
        battery = Battery(13.5, initial_soc=0.3).state  # 30% > 20% minimum
        
        action = engine.decide(env, battery)
        
        # 30% is below peak threshold (40%) but above minimum (20%), so still discharge
        assert action == Action.DISCHARGE_BATTERY
    
    def test_normal_hours_discharge_if_above_minimum(self):
        """During normal hours, discharge if SOC > 20%."""
        engine = DecisionEngine()
        env = EnvironmentState(hour=14, solar_kwh=2.0, load_kwh=5.0, price=0.18)
        battery = Battery(13.5, initial_soc=0.3).state  # 30% > 20% minimum
        
        action = engine.decide(env, battery)
        
        assert action == Action.DISCHARGE_BATTERY
    
    def test_normal_hours_use_grid_if_at_minimum(self):
        """During normal hours with SOC at minimum, use grid."""
        engine = DecisionEngine()
        env = EnvironmentState(hour=14, solar_kwh=2.0, load_kwh=5.0, price=0.18)
        battery = Battery(13.5, initial_soc=0.2).state  # Exactly at minimum
        
        action = engine.decide(env, battery)
        
        # At exactly minimum, policy says use grid
        assert action == Action.USE_GRID
    
    def test_night_hours_use_battery_if_available(self):
        """During night hours, use battery if above minimum."""
        engine = DecisionEngine()
        env = EnvironmentState(hour=2, solar_kwh=0.0, load_kwh=3.0, price=0.12)
        battery = Battery(13.5, initial_soc=0.5).state
        
        action = engine.decide(env, battery)
        
        assert action == Action.DISCHARGE_BATTERY


class TestBoundaryConditions:
    """Edge cases and boundary conditions."""
    
    def test_exact_balance_idle(self):
        """When solar exactly equals load, treat as surplus (charge if room)."""
        engine = DecisionEngine()
        env = EnvironmentState(hour=12, solar_kwh=5.0, load_kwh=5.0, price=0.18)
        battery = Battery(13.5, initial_soc=0.5).state
        
        action = engine.decide(env, battery)
        
        # Net = 0, so treated as surplus (no deficit)
        assert action == Action.CHARGE_BATTERY
    
    def test_just_above_peak_threshold_discharges(self):
        """SOC just above 40% should discharge during peak."""
        engine = DecisionEngine()
        env = EnvironmentState(hour=19, solar_kwh=2.0, load_kwh=8.0, price=0.30)
        battery = Battery(13.5, initial_soc=0.41).state  # Just above 40%
        
        action = engine.decide(env, battery)
        
        assert action == Action.DISCHARGE_BATTERY
    
    def test_just_below_peak_threshold_discharges(self):
        """SOC just below 40% but above 20% should still discharge during peak."""
        engine = DecisionEngine()
        env = EnvironmentState(hour=19, solar_kwh=2.0, load_kwh=8.0, price=0.30)
        battery = Battery(13.5, initial_soc=0.39).state  # Just below 40%
        
        action = engine.decide(env, battery)
        
        # 39% is below peak threshold (40%) but above minimum (20%), so discharge
        assert action == Action.DISCHARGE_BATTERY


class TestPriceAwareness:
    """Decision engine should respect pricing signals."""
    
    def test_high_price_prefers_battery(self):
        """During expensive periods, prefer battery over grid."""
        engine = DecisionEngine()
        
        # Same SOC, different hours (peak vs normal)
        battery = Battery(13.5, initial_soc=0.5).state
        
        peak_env = EnvironmentState(hour=19, solar_kwh=2.0, load_kwh=8.0, price=0.30)
        normal_env = EnvironmentState(hour=14, solar_kwh=2.0, load_kwh=8.0, price=0.18)
        
        peak_action = engine.decide(peak_env, battery)
        normal_action = engine.decide(normal_env, battery)
        
        # Both should discharge (SOC > thresholds)
        assert peak_action == Action.DISCHARGE_BATTERY
        assert normal_action == Action.DISCHARGE_BATTERY
    
    def test_low_price_allows_grid(self):
        """During cheap periods, grid usage is acceptable."""
        engine = DecisionEngine()
        env = EnvironmentState(hour=2, solar_kwh=0.0, load_kwh=5.0, price=0.12)
        battery = Battery(13.5, initial_soc=0.15).state  # Below minimum
        
        action = engine.decide(env, battery)
        
        assert action == Action.USE_GRID


class TestConservationMode:
    """Conservation mode recommendations."""
    
    def test_evening_low_battery_cloudy_conservation(self):
        """Late evening + low battery + cloudy = conserve."""
        engine = DecisionEngine()
        battery = Battery(13.5, initial_soc=0.25).state
        
        should_conserve = engine.should_conserve_energy(21, battery, tomorrow_cloudy=True)
        
        assert should_conserve is True
    
    def test_critical_battery_conservation(self):
        """SOC below 15% triggers conservation regardless of other factors."""
        engine = DecisionEngine()
        battery = Battery(13.5, initial_soc=0.10).state
        
        should_conserve = engine.should_conserve_energy(12, battery, tomorrow_cloudy=False)
        
        assert should_conserve is True
    
    def test_adequate_battery_no_conservation(self):
        """Good battery level means no conservation needed."""
        engine = DecisionEngine()
        battery = Battery(13.5, initial_soc=0.6).state
        
        should_conserve = engine.should_conserve_energy(21, battery, tomorrow_cloudy=True)
        
        assert should_conserve is False
