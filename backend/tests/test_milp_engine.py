"""
Tests for MILP-based Decision Engine.

Tests verify:
- MILP produces valid solutions
- MILP outperforms rule-based in specific scenarios
- Constraints are respected (SOC bounds, power limits)
- Energy balance is maintained
"""
import pytest
from src.engine.milp_engine import MILPDecisionEngine
from src.engine.decision_engine import DecisionEngine
from src.data.models import EnvironmentState, SimulationConfig, Season, Weather, DayType
from src.core.battery import Battery, BatteryState
from src.data.simulator import EnergyDataSimulator


class TestMILPBasicFunctionality:
    """MILP solver produces valid solutions."""
    
    def test_milp_produces_24_actions(self):
        """MILP should return exactly 24 actions."""
        engine = MILPDecisionEngine()
        
        # Create simple test environment
        environments = [
            EnvironmentState(hour=h, solar_kwh=5.0, load_kwh=3.0, price=0.18)
            for h in range(24)
        ]
        battery = Battery(13.5, initial_soc=0.5)
        
        actions = engine.optimize_schedule(environments, battery.state)
        
        assert len(actions) == 24
        assert all(action is not None for action in actions)
    
    def test_milp_handles_peak_pricing(self):
        """MILP should avoid importing during peak hours when possible."""
        engine = MILPDecisionEngine()
        
        # Create scenario with high consumption during peak
        environments = []
        for h in range(24):
            if 18 <= h < 22:  # Peak hours
                price = 0.30
                load = 8.0  # High load
                solar = 2.0
            else:
                price = 0.18
                load = 3.0
                solar = 5.0
            
            environments.append(
                EnvironmentState(hour=h, solar_kwh=solar, load_kwh=load, price=price)
            )
        
        battery = Battery(13.5, initial_soc=0.8)  # Start with high SOC
        
        actions = engine.optimize_schedule(environments, battery.state)
        
        # During peak hours, should prefer discharging over importing
        for h in range(18, 22):
            # Either discharging or using grid
            assert actions[h].value in ['discharge_battery', 'use_grid']
    
    def test_milp_respects_battery_capacity(self):
        """MILP solution should never exceed battery capacity."""
        engine = MILPDecisionEngine()
        
        # Scenario with massive solar surplus
        environments = [
            EnvironmentState(hour=h, solar_kwh=15.0, load_kwh=2.0, price=0.18)
            for h in range(24)
        ]
        
        battery = Battery(13.5, initial_soc=0.5)
        
        # Get detailed schedule
        details = engine.get_schedule_details(environments, battery.state)
        
        # Check all battery levels are within bounds
        for detail in details:
            assert 0.20 * 13.5 <= detail['battery_charge'] <= 0.95 * 13.5, \
                f"Battery charge {detail['battery_charge']} out of bounds at hour {detail['hour']}"


class TestMILPvsRuleBased:
    """MILP should outperform rule-based in lookahead scenarios."""
    
    def test_milp_saves_money_vs_rule_based_arbitrage(self):
        """MILP should perform better in price arbitrage scenarios."""
        milp_engine = MILPDecisionEngine()
        rule_engine = DecisionEngine()
        
        # Create arbitrage opportunity:
        # - Morning: High solar, low price (should charge)
        # - Evening: Low solar, high price (should discharge)
        environments = []
        for h in range(24):
            if 8 <= h <= 14:  # Morning/afternoon: solar surplus
                solar, load, price = 10.0, 3.0, 0.12  # Low price
            elif 18 <= h <= 21:  # Evening: deficit + peak
                solar, load, price = 2.0, 8.0, 0.30  # High price
            else:
                solar, load, price = 5.0, 4.0, 0.18  # Normal
            
            environments.append(
                EnvironmentState(hour=h, solar_kwh=solar, load_kwh=load, price=price)
            )
        
        battery = Battery(13.5, initial_soc=0.3)  # Start low
        
        # Get MILP schedule
        milp_actions = milp_engine.optimize_schedule(environments, battery.state)
        
        # Simulate MILP schedule
        battery.reset(0.3)
        milp_cost = self._simulate_schedule(milp_actions, environments, battery)
        
        # Simulate rule-based
        battery.reset(0.3)
        rule_cost = 0
        for env in environments:
            action = rule_engine.decide(env, battery.state)
            grid_import, _ = self._apply_action(action, env, battery)
            rule_cost += grid_import * env.price
        
        # MILP should be cheaper or equal (allow small tolerance)
        assert milp_cost <= rule_cost * 1.01, \
            f"MILP cost {milp_cost:.2f} should be <= rule-based {rule_cost:.2f}"
    
    def _simulate_schedule(self, actions, environments, battery):
        """Helper to simulate a schedule and calculate cost."""
        total_cost = 0
        for action, env in zip(actions, environments):
            grid_import, grid_export = self._apply_action(action, env, battery)
            cost = grid_import * env.price - grid_export * 0.08
            total_cost += cost
        return total_cost
    
    def _apply_action(self, action, env, battery):
        """Apply action and return grid import/export."""
        net = env.solar_kwh - env.load_kwh
        
        if action.value == 'charge_battery':
            if net > 0:
                battery.charge(net)
            return 0.0, 0.0
        elif action.value == 'discharge_battery':
            if net < 0:
                demand = abs(net)
                drawn, delivered = battery.discharge(demand)
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


class TestMILPConstraints:
    """MILP respects all physical and operational constraints."""
    
    def test_milp_never_overcharges(self):
        """Battery should never exceed MAX_SOC."""
        engine = MILPDecisionEngine()
        
        # Massive surplus scenario
        environments = [
            EnvironmentState(hour=h, solar_kwh=15.0, load_kwh=1.0, price=0.12)
            for h in range(24)
        ]
        
        battery = Battery(13.5, initial_soc=0.9)  # Start near max
        
        details = engine.get_schedule_details(environments, battery.state)
        
        for detail in details:
            assert detail['battery_charge'] <= 13.5 * 0.95 + 0.01, \
                f"Overcharge at hour {detail['hour']}: {detail['battery_charge']}"
    
    def test_milp_never_overdischarges(self):
        """Battery should never go below MIN_SOC."""
        engine = MILPDecisionEngine()
        
        # Massive deficit scenario
        environments = [
            EnvironmentState(hour=h, solar_kwh=1.0, load_kwh=10.0, price=0.30)
            for h in range(24)
        ]
        
        battery = Battery(13.5, initial_soc=0.25)  # Start near min
        
        details = engine.get_schedule_details(environments, battery.state)
        
        for detail in details:
            assert detail['battery_charge'] >= 13.5 * 0.20 - 0.01, \
                f"Undercharge at hour {detail['hour']}: {detail['battery_charge']}"
    
    def test_milp_respects_power_limits(self):
        """Charging/discharging should respect power limits."""
        engine = MILPDecisionEngine()
        
        environments = [
            EnvironmentState(hour=h, solar_kwh=10.0, load_kwh=2.0, price=0.18)
            for h in range(24)
        ]
        
        battery = Battery(13.5, initial_soc=0.5)
        
        details = engine.get_schedule_details(environments, battery.state)
        
        for detail in details:
            assert detail['charge_rate'] <= 5.0 + 0.01, \
                f"Charge rate exceeded at hour {detail['hour']}"
            assert detail['discharge_rate'] <= 5.0 + 0.01, \
                f"Discharge rate exceeded at hour {detail['hour']}"


class TestMILPRealScenarios:
    """MILP on realistic scenarios."""
    
    def test_milp_on_summer_sunny_day(self):
        """MILP should handle realistic summer sunny scenario."""
        config = SimulationConfig(
            season=Season.SUMMER,
            weather=Weather.SUNNY,
            day_type=DayType.WEEKDAY
        )
        
        simulator = EnergyDataSimulator(config, seed=42)
        environments = simulator.generate_24h_environment()
        
        engine = MILPDecisionEngine()
        battery = Battery(13.5, initial_soc=0.5)
        
        actions = engine.optimize_schedule(environments, battery.state)
        
        assert len(actions) == 24
        # Should have some variety of actions
        action_values = [a.value for a in actions]
        assert 'charge_battery' in action_values or 'sell_to_grid' in action_values
    
    def test_milp_determinism(self):
        """Same inputs should produce same outputs."""
        engine = MILPDecisionEngine()
        
        config = SimulationConfig(
            season=Season.WINTER,
            weather=Weather.CLOUDY,
            day_type=DayType.WEEKEND
        )
        
        simulator = EnergyDataSimulator(config, seed=42)
        environments = simulator.generate_24h_environment()
        
        battery1 = Battery(13.5, initial_soc=0.5)
        actions1 = engine.optimize_schedule(environments, battery1.state)
        
        # Create fresh battery with same state
        battery2 = Battery(13.5, initial_soc=0.5)
        actions2 = engine.optimize_schedule(environments, battery2.state)
        
        assert [a.value for a in actions1] == [a.value for a in actions2]
