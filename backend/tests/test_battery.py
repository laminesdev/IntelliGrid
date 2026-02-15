"""
Unit tests for Battery class.

Tests cover:
- Energy conservation (battery cannot create energy)
- SOC bounds enforcement
- Efficiency calculations
"""
import pytest
from src.core.battery import Battery, BatteryState


class TestEnergyConservation:
    """Battery physics must conserve energy (with efficiency losses)."""
    
    def test_charge_efficiency_reduces_stored_energy(self):
        """When charging, stored energy is less than consumed due to efficiency."""
        battery = Battery(13.5, initial_soc=0.5)
        available = 10.0
        
        consumed, stored = battery.charge(available)
        
        assert stored < consumed, "Stored energy should be less than consumed due to efficiency loss"
        assert stored == pytest.approx(consumed * Battery.CHARGE_EFFICIENCY), \
            "Stored energy should equal consumed * efficiency"
    
    def test_discharge_efficiency_reduces_delivered_energy(self):
        """When discharging, delivered energy is less than drawn due to efficiency."""
        battery = Battery(13.5, initial_soc=0.8)
        demand = 5.0
        
        drawn, delivered = battery.discharge(demand)
        
        assert delivered < drawn, "Delivered energy should be less than drawn due to efficiency loss"
        assert delivered == pytest.approx(drawn * Battery.DISCHARGE_EFFICIENCY), \
            "Delivered energy should equal drawn * efficiency"
    
    def test_round_trip_loses_energy(self):
        """Complete charge-discharge cycle results in net energy loss."""
        battery = Battery(13.5, initial_soc=0.5)
        initial_charge = battery.charge_kwh
        
        # Charge some energy
        charge_amount = 5.0
        battery.charge(charge_amount)
        after_charge = battery.charge_kwh
        
        # Discharge the same amount we stored
        stored_energy = after_charge - initial_charge
        battery.discharge(stored_energy)
        
        # After full cycle, we should have less than we started with
        assert battery.charge_kwh < initial_charge, \
            "Round-trip should lose energy due to efficiency losses"
    
    def test_no_energy_creation_on_charge(self):
        """Cannot store more energy than provided."""
        battery = Battery(13.5, initial_soc=0.5)
        available = 3.0
        
        consumed, stored = battery.charge(available)
        
        assert consumed <= available, "Cannot consume more than available"
        assert stored <= available, "Cannot store more than available"
    
    def test_no_energy_creation_on_discharge(self):
        """Cannot deliver more energy than battery contains."""
        battery = Battery(13.5, initial_soc=0.5)
        
        # Try to discharge huge amount
        demand = 100.0
        drawn, delivered = battery.discharge(demand)
        
        max_possible_draw = 0.5 * 13.5 - 0.2 * 13.5  # SOC - MIN_SOC
        assert drawn <= max_possible_draw + 0.001, \
            "Cannot draw more energy than available above MIN_SOC"


class TestSOCBounds:
    """SOC must stay within [MIN_SOC, MAX_SOC]."""
    
    def test_soc_never_exceeds_max(self):
        """Charging cannot push SOC above MAX_SOC."""
        battery = Battery(13.5, initial_soc=0.94)  # Just below MAX
        
        # Try to massively overcharge
        battery.charge(100.0)
        
        assert battery.state.soc <= Battery.MAX_SOC + 0.001, \
            f"SOC should not exceed MAX_SOC ({Battery.MAX_SOC})"
    
    def test_soc_never_falls_below_min(self):
        """Discharging cannot push SOC below MIN_SOC."""
        battery = Battery(13.5, initial_soc=0.21)  # Just above MIN
        
        # Try to massively over-discharge
        battery.discharge(100.0)
        
        assert battery.state.soc >= Battery.MIN_SOC - 0.001, \
            f"SOC should not fall below MIN_SOC ({Battery.MIN_SOC})"
    
    def test_initial_soc_validation(self):
        """Invalid initial SOC should raise error."""
        with pytest.raises(ValueError):
            Battery(13.5, initial_soc=-0.1)
        
        with pytest.raises(ValueError):
            Battery(13.5, initial_soc=1.5)
    
    def test_charge_at_max_soc_does_nothing(self):
        """Charging when at MAX_SOC should store nothing."""
        battery = Battery(13.5, initial_soc=Battery.MAX_SOC)
        
        consumed, stored = battery.charge(10.0)
        
        assert consumed == 0.0, "Should consume nothing when at MAX_SOC"
        assert stored == 0.0, "Should store nothing when at MAX_SOC"
    
    def test_discharge_at_min_soc_does_nothing(self):
        """Discharging when at MIN_SOC should deliver nothing."""
        battery = Battery(13.5, initial_soc=Battery.MIN_SOC)
        
        drawn, delivered = battery.discharge(10.0)
        
        assert drawn == 0.0, "Should draw nothing when at MIN_SOC"
        assert delivered == 0.0, "Should deliver nothing when at MIN_SOC"


class TestPowerLimits:
    """Charge/discharge rate limits must be respected."""
    
    def test_charge_respects_max_rate(self):
        """Charging cannot exceed MAX_CHARGE_RATE."""
        battery = Battery(13.5, initial_soc=0.5)
        
        # Try to charge massive amount
        consumed, stored = battery.charge(100.0)
        
        assert consumed <= Battery.MAX_CHARGE_RATE_KW + 0.001, \
            f"Should not exceed max charge rate ({Battery.MAX_CHARGE_RATE_KW} kW)"
    
    def test_discharge_respects_max_rate(self):
        """Discharging cannot exceed MAX_DISCHARGE_RATE."""
        battery = Battery(13.5, initial_soc=0.8)
        
        # Try to discharge massive amount
        drawn, delivered = battery.discharge(100.0)
        
        assert drawn <= Battery.MAX_DISCHARGE_RATE_KW + 0.001, \
            f"Should not exceed max discharge rate ({Battery.MAX_DISCHARGE_RATE_KW} kW)"


class TestStateImmutability:
    """BatteryState should be immutable snapshot."""
    
    def test_state_does_not_change_after_modification(self):
        """Getting state then modifying battery should not affect old state."""
        battery = Battery(13.5, initial_soc=0.5)
        
        # Get initial state
        state1 = battery.state
        initial_soc = state1.soc
        
        # Modify battery
        battery.charge(5.0)
        
        # Old state should be unchanged
        assert state1.soc == initial_soc, "State should be immutable"
        assert battery.state.soc > initial_soc, "Current state should reflect change"


class TestEdgeCases:
    """Edge cases and boundary conditions."""
    
    def test_charge_with_zero_available(self):
        """Charging with 0 available should do nothing."""
        battery = Battery(13.5, initial_soc=0.5)
        
        consumed, stored = battery.charge(0.0)
        
        assert consumed == 0.0
        assert stored == 0.0
        assert battery.state.soc == 0.5
    
    def test_discharge_with_zero_demand(self):
        """Discharging with 0 demand should do nothing."""
        battery = Battery(13.5, initial_soc=0.5)
        
        drawn, delivered = battery.discharge(0.0)
        
        assert drawn == 0.0
        assert delivered == 0.0
        assert battery.state.soc == 0.5
    
    def test_negative_charge_does_nothing(self):
        """Negative charge input should be treated as zero."""
        battery = Battery(13.5, initial_soc=0.5)
        
        consumed, stored = battery.charge(-5.0)
        
        assert consumed == 0.0
        assert stored == 0.0
    
    def test_negative_discharge_does_nothing(self):
        """Negative discharge demand should be treated as zero."""
        battery = Battery(13.5, initial_soc=0.5)
        
        drawn, delivered = battery.discharge(-5.0)
        
        assert drawn == 0.0
        assert delivered == 0.0
    
    def test_partial_charge_due_to_soc_limit(self):
        """Charge should be limited by SOC, not just available energy."""
        battery = Battery(13.5, initial_soc=0.9)  # Near max
        
        # Lots of available energy, but limited by SOC
        consumed, stored = battery.charge(100.0)
        
        # Should charge up to MAX_SOC
        assert battery.state.soc <= Battery.MAX_SOC + 0.001
        # Should not have consumed all available energy
        assert consumed < 100.0
    
    def test_partial_discharge_due_to_soc_limit(self):
        """Discharge should be limited by SOC, not just demand."""
        battery = Battery(13.5, initial_soc=0.3)  # Near min
        
        # Lots of demand, but limited by SOC
        drawn, delivered = battery.discharge(100.0)
        
        # Should discharge down to MIN_SOC
        assert battery.state.soc >= Battery.MIN_SOC - 0.001
        # Should not have drawn enough to meet demand
        assert delivered < 100.0
