"""
Battery Diagnostic Script - Identify why battery stays at 0.6%

This script tests:
1. AI model predictions (solar & consumption)
2. Battery charge/discharge behavior
3. Scale issues (are predictions 100x too small?)
4. Energy flow through the system

Run from backend/ directory:
    cd /home/lamine/Projects/IntelliGrid/backend
    source venv/bin/activate
    python -m scripts.diagnose_battery
"""
import sys
from pathlib import Path

# Add backend to path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Now imports will work with 'backend.src.xxx' or 'src.xxx'
try:
    from src.ai.model_manager import ModelManager
    from src.ai.solar_predictor import SolarPredictor
    from src.ai.consumption_predictor import ConsumptionPredictor
    from src.data.models import SimulationConfig, Season, Weather, DayType
    from src.data.simulator import EnergyDataSimulator
    from src.core.battery import Battery
    from src.core.simulation_runner import SimulationRunner
    from src.engine.decision_engine import DecisionEngine
except ImportError as e:
    print(f"Import error: {e}")
    print("Trying alternative import path...")
    # Try relative to backend
    sys.path.insert(0, str(backend_dir.parent))
    from backend.src.ai.model_manager import ModelManager
    from backend.src.ai.solar_predictor import SolarPredictor
    from backend.src.data.models import SimulationConfig, Season, Weather, DayType
    from backend.src.data.simulator import EnergyDataSimulator
    from backend.src.core.battery import Battery
    from backend.src.engine.decision_engine import DecisionEngine

def test_ai_predictions():
    """Test 1: Check AI model output scales"""
    print("=" * 70)
    print("TEST 1: AI Model Predictions - Checking Scale")
    print("=" * 70)
    
    manager = ModelManager()
    
    print("\n📊 Model Status:")
    status = manager.get_model_status()
    print(f"  Solar: Loaded={status['solar']['loaded']}, Fallback={status['solar']['using_fallback']}")
    print(f"  Consumption: Loaded={status['consumption']['loaded']}, Fallback={status['consumption']['using_fallback']}")
    
    print("\n🌅 Predictions for Sample Hours (Summer, Sunny, Weekday):")
    print("-" * 70)
    print(f"{'Hour':<6} {'Solar (kW)':<12} {'Cons (kW)':<12} {'Net (kW)':<12} {'Batt Δ%':<12}")
    print("-" * 70)
    
    battery_capacity = 13.5  # kWh
    
    test_hours = [0, 6, 9, 12, 15, 18, 21]
    for hour in test_hours:
        pred = manager.get_predictions(
            hour=hour,
            day=15,
            month=6,  # June = summer
            weather='sunny',
            season='summer'
        )
        
        solar = pred['solar_kw']
        cons = pred['consumption_kw']
        net = pred['net_kw']
        
        # Calculate battery change percentage
        # If net is in kW (power), and we apply it for 1 hour = kWh (energy)
        battery_delta_pct = (net / battery_capacity) * 100
        
        print(f"{hour:<6} {solar:<12.4f} {cons:<12.4f} {net:<12.4f} {battery_delta_pct:<12.2f}%")
    
    print("-" * 70)
    print("\n📈 Summary:")
    print(f"  Battery Capacity: {battery_capacity} kWh")
    print(f"  Max possible change per hour: {(5.0 / battery_capacity) * 100:.2f}% (limited by 5kW charge rate)")
    print(f"  If solar=0.05 kW and cons=0.03 kW, net=0.02 kW")
    print(f"  Battery change: {(0.02 / battery_capacity) * 100:.3f}% per hour")
    print(f"  After 24 hours: {(0.02 * 24 / battery_capacity) * 100:.3f}% (THIS IS THE BUG!)")
    
    return manager

def test_battery_directly():
    """Test 2: Test battery with realistic vs tiny values"""
    print("\n" + "=" * 70)
    print("TEST 2: Battery Behavior - Realistic vs Tiny Values")
    print("=" * 70)
    
    battery = Battery(capacity_kwh=13.5, initial_soc=0.5)
    
    print("\n🔋 Scenario A: REALISTIC Values (Solar=8kW, Cons=2kW)")
    print("-" * 70)
    
    # Realistic: High solar, low consumption
    net_realistic = 8.0 - 2.0  # 6 kW surplus
    print(f"  Net power: {net_realistic} kW")
    
    consumed, stored = battery.charge(net_realistic)
    print(f"  Energy consumed: {consumed:.4f} kWh")
    print(f"  Energy stored: {stored:.4f} kWh")
    print(f"  New SOC: {battery.state.soc * 100:.2f}%")
    
    battery.reset(0.5)  # Reset
    
    print("\n🔋 Scenario B: TINY Values (Solar=0.08kW, Cons=0.05kW) - LIKELY BUG")
    print("-" * 70)
    
    # Tiny: Low solar, low consumption (100x too small!)
    net_tiny = 0.08 - 0.05  # 0.03 kW surplus
    print(f"  Net power: {net_tiny} kW (100x too small!)")
    
    consumed, stored = battery.charge(net_tiny)
    print(f"  Energy consumed: {consumed:.4f} kWh")
    print(f"  Energy stored: {stored:.4f} kWh")
    print(f"  New SOC: {battery.state.soc * 100:.2f}%")
    print(f"  Expected if scaled correctly: ~{(0.5 + (3.0/13.5)) * 100:.2f}%")
    
    return battery

def test_full_simulation_trace():
    """Test 3: Trace full simulation with logging"""
    print("\n" + "=" * 70)
    print("TEST 3: Full Simulation - First 6 Hours Trace")
    print("=" * 70)
    
    config = SimulationConfig(
        season=Season.SUMMER,
        weather=Weather.SUNNY,
        day_type=DayType.WEEKDAY
    )
    
    simulator = EnergyDataSimulator(config, seed=42, use_ai=True)
    battery = Battery(capacity_kwh=13.5, initial_soc=0.5)  # Start at 50%
    engine = DecisionEngine()
    runner = SimulationRunner(simulator, engine, battery)
    
    print(f"\n🔋 Initial Battery SOC: {battery.state.soc * 100:.2f}%")
    print("-" * 70)
    print(f"{'Hour':<6} {'Solar':<10} {'Load':<10} {'Net':<10} {'Action':<20} {'Batt%':<10}")
    print("-" * 70)
    
    # Run only first 6 hours
    env_data = simulator.generate_24h_environment()[:6]
    
    for env in env_data:
        action = engine.decide(env, battery.state)
        
        # Apply action
        if action.value == "charge_battery":
            if env.solar_kwh > env.load_kwh:
                surplus = env.solar_kwh - env.load_kwh
                battery.charge(surplus)
        elif action.value == "discharge_battery":
            if env.load_kwh > env.solar_kwh:
                deficit = env.load_kwh - env.solar_kwh
                battery.discharge(deficit)
        
        print(f"{env.hour:<6} {env.solar_kwh:<10.4f} {env.load_kwh:<10.4f} "
              f"{env.solar_kwh - env.load_kwh:<10.4f} {action.value:<20} "
              f"{battery.state.soc * 100:<10.2f}%")
    
    print("-" * 70)
    print(f"🔋 Final Battery SOC after 6 hours: {battery.state.soc * 100:.2f}%")
    
    if battery.state.soc < 0.52:  # Should be at least 52% if charging
        print("\n❌ BUG CONFIRMED: Battery barely changed!")
        print("   Expected: ~70-80% after charging during sunny morning")
        print("   Actual: {:.2f}%".format(battery.state.soc * 100))
        print("\n🔧 FIX NEEDED: Scale factor on AI predictions (multiply by ~100)")
    else:
        print("\n✅ Battery charging normally")

def check_model_scale_factor():
    """Test 4: Check if we need scale factor"""
    print("\n" + "=" * 70)
    print("TEST 4: Checking Model Output Scale Factor")
    print("=" * 70)
    
    solar = SolarPredictor()
    
    # Test at peak solar hour (noon)
    print("\n☀️  Solar Model - Peak Hour Test (Summer, Sunny, 12:00):")
    pred = solar.predict(
        hour=12,
        day=15,
        month=6,
        weather='sunny',
        season='summer'
    )
    
    print(f"  Predicted solar: {pred:.6f} kW")
    print(f"  Expected realistic: ~8-10 kW")
    
    if pred < 0.1:  # Less than 0.1 kW = 100W (way too small!)
        scale_factor = 10.0 / pred  # How much to multiply to get 10 kW
        print(f"\n❌ OUTPUT IS {pred:.6f} kW - WAY TOO SMALL!")
        print(f"   Needs scale factor: ×{scale_factor:.1f}")
        print(f"   After scaling: {pred * scale_factor:.2f} kW ✓")
        return scale_factor
    elif pred > 5.0:
        print(f"\n✅ OUTPUT IS {pred:.2f} kW - GOOD SCALE")
        return 1.0
    else:
        scale_factor = 10.0 / pred
        print(f"\n⚠️  OUTPUT IS {pred:.2f} kW - SMALLISH")
        print(f"   Suggested scale factor: ×{scale_factor:.1f}")
        return scale_factor

def main():
    """Run all diagnostic tests"""
    print("\n" + "=" * 70)
    print("🔋 BATTERY DIAGNOSTIC - IntelliGrid AI Model Integration")
    print("=" * 70)
    
    try:
        # Run all tests
        manager = test_ai_predictions()
        battery = test_battery_directly()
        scale_factor = check_model_scale_factor()
        test_full_simulation_trace()
        
        # Final recommendations
        print("\n" + "=" * 70)
        print("📋 DIAGNOSTIC SUMMARY & RECOMMENDATIONS")
        print("=" * 70)
        
        if scale_factor > 10:
            print("\n🔴 ROOT CAUSE IDENTIFIED: AI Model Output Scale")
            print(f"   Models output values ~{scale_factor}x too small")
            print(f"   FIX: Multiply predictions by {scale_factor:.1f}")
            print("\n   Files to modify:")
            print("   - src/ai/solar_predictor.py (line 137)")
            print("   - src/ai/consumption_predictor.py (line 117)")
        else:
            print("\n🟡 Scale looks reasonable, checking other issues...")
        
        print("\n✅ Diagnostic complete!")
        
    except Exception as e:
        print(f"\n❌ Error during diagnostic: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
