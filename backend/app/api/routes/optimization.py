"""
Optimization routes - comparing rule-based vs MILP.
"""
from fastapi import APIRouter, HTTPException
import traceback

from app.models import SimulationConfig, SimulationResponse, ComparisonResponse, OptimizationMode
from app.services.simulation import SimulationService
from app.logging_config import logger

router = APIRouter()


@router.post("/optimize", response_model=SimulationResponse)
async def run_optimization(config: SimulationConfig):
    """
    Run MILP optimization.
    
    This endpoint runs the MILP (Mixed Integer Linear Programming) optimizer
    which provides globally optimal battery scheduling over the 24-hour horizon.
    
    Args:
        config: Simulation configuration (mode will be overridden to 'milp')
        
    Returns:
        Optimized simulation results
    """
    try:
        # Force MILP mode
        config.mode = OptimizationMode.MILP
        result = SimulationService.run_simulation(config)
        return result
    except Exception as e:
        logger.error(f"Error in optimization: {e}")
        logger.debug(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare")
async def compare_optimizations(config: SimulationConfig):
    """
    Compare rule-based vs MILP optimization.
    
    Runs both optimization methods with the same configuration and returns
    a comparison showing cost savings and decision differences.
    
    Returns:
        {
            "rule_result": SimulationResponse,
            "milp_result": SimulationResponse,
            "cost_savings": float,
            "improvement_percent": float,
            "different_decisions_count": int
        }
    """
    try:
        comparison = SimulationService.compare_optimizations(config)
        return comparison
    except Exception as e:
        logger.error(f"Error in comparison: {e}")
        logger.debug(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/compare/test")
async def test_comparison():
    """Test comparison with default config."""
    from app.models import SimulationConfig
    config = SimulationConfig()
    return await compare_optimizations(config)
