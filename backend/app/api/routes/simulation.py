"""
Simulation routes.
"""
from fastapi import APIRouter, HTTPException
import traceback

from app.models import SimulationConfig, SimulationResponse
from app.services.simulation import SimulationService
from app.logging_config import logger

router = APIRouter()


@router.post("/simulate", response_model=SimulationResponse)
async def run_simulation(config: SimulationConfig):
    """
    Run a single energy simulation.
    
    Args:
        config: Simulation configuration including season, weather, day type, and optimization mode
        
    Returns:
        Hour-by-hour simulation results with totals
        
    Example:
        ```json
        {
            "season": "summer",
            "weather": "sunny",
            "day_type": "weekday",
            "mode": "rule",
            "seed": 42
        }
        ```
    """
    try:
        result = SimulationService.run_simulation(config)
        return result
    except Exception as e:
        logger.error(f"Error in simulation: {e}")
        logger.debug(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/simulate/test")
async def test_simulation():
    """Test endpoint with default config."""
    config = SimulationConfig()
    return await run_simulation(config)
