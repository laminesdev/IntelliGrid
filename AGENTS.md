# IntelliGrid - Agent Guidelines

## Project Overview
Smart Home Energy Management System built with Python and Streamlit. Uses predictive energy optimization with dynamic pricing and battery intelligence.

## Build/Run Commands

### Run Application
```bash
streamlit run app.py
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run on Different Port
```bash
streamlit run app.py --server.port 8502
```

## Testing (UPDATED)

### Test Framework Configured ✅
This project now has comprehensive test coverage using pytest.

**Activate virtual environment first:**
```bash
source venv/bin/activate
```

**Run all tests:**
```bash
pytest
# or
python -m pytest tests/ -v
```

**Run specific test file:**
```bash
pytest tests/test_battery.py
pytest tests/test_decision_engine.py
pytest tests/test_integration.py
```

**Run single test:**
```bash
pytest tests/test_battery.py::TestEnergyConservation::test_round_trip_loses_energy
pytest tests/test_decision_engine.py::TestDeficitScenarios::test_peak_hours_discharge
```

**Run with coverage:**
```bash
pytest --cov=src --cov-report=html
```

**Current Test Status:**
- Total: 52 tests
- Battery tests: 19 (physics correctness)
- Decision engine tests: 16 (policy logic)
- MILP engine tests: 9 (optimization)
- Integration tests: 8 (end-to-end)
- All passing ✅

## Architecture (UPDATED)

### Clean Architecture

The codebase follows a decoupled architecture:

```
src/
├── core/          # Physics and orchestration
│   ├── battery.py              # Battery physics (stateful)
│   ├── simulation_runner.py    # Orchestrates simulation
│   ├── adapter.py              # Backward compatibility
│   └── hybrid_adapter.py       # Rule vs MILP comparison
├── data/          # Data simulation and models
│   ├── simulator.py            # Generates environment only
│   └── models.py               # Dataclasses and enums
├── engine/        # Business logic
│   ├── decision_engine.py      # Policy-based decisions
│   ├── milp_engine.py          # MILP optimization (Phase C)
│   └── weather_predictor.py
├── analysis/      # Impact calculations
├── ui/           # Streamlit components
└── utils/        # Configuration
```

### Key Architectural Principles

**1. Separation of Concerns**
- Simulator generates environment (solar, load, price) - NO decisions
- Decision engine chooses actions (policy) - NO physics
- Battery applies physics (charge/discharge) - NO decisions
- Runner orchestrates the flow

**2. Immutable State**
- `EnvironmentState` - snapshot of conditions
- `BatteryState` - snapshot of battery
- Pass state objects, not raw values

**3. Reproducibility**
- All randomness uses seeded RNG
- Same seed = identical results
- Seed stored in simulation results

### MILP Optimization (Phase C)

The project now includes Mixed Integer Linear Programming (MILP) optimization:

**MILP vs Rule-Based:**
- Rule-based: Greedy hour-by-hour decisions (fast)
- MILP: Global optimization over 24-hour horizon (optimal)

**When MILP Wins:**
- Price arbitrage (low price charge, high price discharge)
- Complex constraint satisfaction
- Time-coupled decisions

**Usage:**
```python
from src.core.hybrid_adapter import HybridSimulationAdapter

# Rule-based (fast, greedy)
adapter = HybridSimulationAdapter(config, seed=42, mode='rule')
result = adapter.generate_24h_data()

# MILP (optimal, slower)
adapter = HybridSimulationAdapter(config, seed=42, mode='milp')
result = adapter.generate_24h_data()

# Compare both
comparison = adapter.compare_modes()
# Returns: {'rule_cost': X, 'milp_cost': Y, 'savings': Z, ...}
```

**Run comparison demo:**
```bash
source venv/bin/activate
python demo_milp_comparison.py
```

### Example Usage (New Architecture)

```python
from src.data.models import SimulationConfig, Season, Weather, DayType
from src.core.adapter import SimulationAdapter

# Configure
config = SimulationConfig(
    season=Season.SUMMER,
    weather=Weather.SUNNY,
    day_type=DayType.WEEKDAY
)

# Run simulation (backward compatible)
adapter = SimulationAdapter(config, seed=42)
result = adapter.generate_24h_data()

# Or use components directly
from src.data.simulator import EnergyDataSimulator
from src.engine.decision_engine import DecisionEngine
from src.core.battery import Battery
from src.core.simulation_runner import SimulationRunner

simulator = EnergyDataSimulator(config, seed=42)
battery = Battery(capacity_kwh=13.5, initial_soc=0.5)
engine = DecisionEngine()
runner = SimulationRunner(simulator, engine, battery)
result = runner.run()
```

## Code Style Guidelines

### Import Order
1. Standard library imports
2. Third-party imports (streamlit, pandas, numpy, plotly)
3. Local imports

Example:
```python
from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass
from enum import Enum

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from src.core.battery import Battery, BatteryState
from src.data.models import SimulationConfig, EnvironmentState
from src.engine.decision_engine import DecisionEngine
```

### Naming Conventions
- **Classes**: PascalCase (e.g., `DecisionEngine`, `SimulationConfig`)
- **Functions/Variables**: snake_case (e.g., `calculate_savings`, `battery_level`)
- **Constants**: UPPER_CASE (e.g., `CHARGE_EFFICIENCY`, `MAX_SOC`)
- **Enums**: PascalCase for class, UPPER_CASE for members
- **Private methods**: Leading underscore (e.g., `_handle_surplus`)

### Type Hints
Use type hints for all function parameters and return types:
```python
def decide(
    self,
    env: EnvironmentState,
    battery: BatteryState
) -> Action:
```

### Docstrings
Use Google-style docstrings with Args/Returns sections:
```python
def charge(self, available_kwh: float) -> Tuple[float, float]:
    """Attempt to charge battery from available energy.
    
    Args:
        available_kwh: Energy available for charging in kWh
        
    Returns:
        Tuple of (energy_consumed, energy_stored) in kWh
    """
```

### Error Handling
- Validate inputs at boundaries
- Raise specific exceptions (ValueError, etc.)
- Use try/except at application entry points

Example:
```python
def __init__(self, capacity_kwh: float, initial_soc: float = 0.5):
    if capacity_kwh <= 0:
        raise ValueError("Capacity must be positive")
    if not 0.0 <= initial_soc <= 1.0:
        raise ValueError("Initial SOC must be between 0 and 1")
```

### Formatting
- Line length: 100 characters max
- Use 4 spaces for indentation
- Add blank lines between class methods
- Group related constants together

### Architecture Patterns
- **Modular design**: Separate data, engine, analysis, UI, and core layers
- **Dataclasses**: Use for data models with `@dataclass`
- **Frozen dataclasses**: Use `frozen=True` for immutable state
- **Enums**: Use for categorical types (Weather, Season, Action)
- **Configuration**: Centralize in `src/utils/config.py`
- **Constants**: Use UPPER_CASE in config module and as class attributes

### Battery Physics (IMPORTANT)

**Correct Efficiency Model:**
```python
# Charge: stored = available * efficiency
stored_energy = charge_input * CHARGE_EFFICIENCY  # 0.96

# Discharge: delivered = drawn * efficiency  
delivered_energy = discharge_drawn * DISCHARGE_EFFICIENCY  # 0.96

# Round-trip efficiency: 0.96 * 0.96 = 0.9216 (92.16%)
```

**Never do this (old bug):**
```python
# WRONG - this creates energy
delivered = requested / efficiency  # NO!
```

### File Structure
```
src/
├── core/          # Physics and orchestration (NEW)
├── data/          # Data simulation and models
├── engine/        # Business logic and decision making
├── analysis/      # Impact calculations
├── ui/           # Streamlit components and styling
└── utils/        # Configuration and utilities
tests/
├── test_battery.py           # Battery physics tests
├── test_decision_engine.py   # Decision logic tests
└── test_integration.py       # End-to-end tests
```

### Dependencies
Core stack:
- streamlit==1.28.0 (UI framework)
- pandas==2.0.3 (data manipulation)
- numpy==1.24.3 (numerical computing)
- plotly==5.17.0 (visualizations)
- pytest (testing framework)

## Linting (Recommended)

**Install:**
```bash
pip install flake8 black isort mypy
```

**Run linter:**
```bash
flake8 src/ --max-line-length=100
```

**Format code:**
```bash
black src/ --line-length=100
```

**Sort imports:**
```bash
isort src/ --profile black
```

**Type check:**
```bash
mypy src/
```

## UI Guidelines
- Use Streamlit components from `src/ui/components.py`
- Apply styles from `src/ui/styles.py`
- Use color constants from `COLORS` dict in config
- Add emojis to headers for visual appeal
- Use `unsafe_allow_html=True` for custom HTML components

## Testing Guidelines

**Write tests for:**
1. Battery physics (energy conservation, efficiency, SOC bounds)
2. Decision logic (policy correctness, edge cases)
3. Integration (energy balance, determinism)

**Test naming:**
```python
class TestEnergyConservation:
    def test_charge_efficiency_reduces_stored_energy(self):
        """Descriptive docstring explaining what is tested."""
        # Arrange
        battery = Battery(13.5, initial_soc=0.5)
        
        # Act
        consumed, stored = battery.charge(10.0)
        
        # Assert
        assert stored < consumed
        assert stored == pytest.approx(consumed * 0.96)
```

## Git Workflow
1. Create feature branch
2. Write tests first (TDD approach)
3. Run tests: `pytest tests/ -v`
4. Ensure all tests pass before committing
5. Commit with descriptive messages
6. No pre-commit hooks currently configured

## Important Notes

**Always run tests after changes:**
```bash
source venv/bin/activate
pytest tests/ -v
```

**Never break backward compatibility** without updating the adapter.

**Maintain deterministic behavior** - always use seeded RNG.

**Document breaking changes** in IMPLEMENTATION_SUMMARY.md.
