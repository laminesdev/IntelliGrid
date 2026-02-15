"""
Energy Data Simulator for generating realistic 24-hour environment data.

Now with AI model integration! Uses trained ML models for predictions with simulation fallback.
Generates solar production, consumption, and pricing data WITHOUT making decisions.
Decisions are made by the DecisionEngine, physics by the Battery.

This separation enables:
- Reproducible scenarios (with seed)
- Testing different algorithms on same data
- Replay and debugging
- AI-powered predictions with fallback
"""
from typing import List, Optional
import numpy as np
import logging

from src.data.models import SimulationConfig, EnvironmentState, Season
from src.utils.config import (
    INVERTER_MAX_OUTPUT, SOLAR_SUMMER_PEAK, SOLAR_WINTER_PEAK,
    WEATHER_MULTIPLIERS, CONSUMPTION_BASE_WEEKDAY, CONSUMPTION_BASE_WEEKEND,
    SEASON_MULTIPLIERS, get_price_for_hour, get_consumption_period
)

# Import AI models (with fallback)
try:
    from src.ai.model_manager import ModelManager
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    logging.warning("AI models not available, using simulation only")

logger = logging.getLogger(__name__)


class EnergyDataSimulator:
    """Generates realistic 24-hour environment data (solar, load, prices).
    
    Now uses AI models for predictions with simulation fallback!
    
    This simulator is PURE - it only generates environmental conditions,
    it does NOT make decisions or manage battery state.
    
    Attributes:
        config: Simulation configuration
        rng: Random number generator (reproducible with seed)
        seed: Random seed for reproducibility (stored in results)
        use_ai: Whether to use AI models (if available)
        ai_manager: ModelManager instance for AI predictions
    """
    
    def __init__(self, config: SimulationConfig, seed: Optional[int] = None, use_ai: bool = True):
        """Initialize simulator with configuration.
        
        Args:
            config: SimulationConfig with season, weather, day_type settings
            seed: Random seed for reproducible results
            use_ai: Whether to use AI models (defaults to True, falls back to simulation)
        """
        self.config = config
        self.rng = np.random.default_rng(seed)
        self.seed = seed
        self.use_ai = use_ai and AI_AVAILABLE
        self.ai_manager = None
        
        # Initialize AI manager if requested
        if self.use_ai:
            try:
                self.ai_manager = ModelManager()
                solar_fallback = self.ai_manager.solar.is_using_fallback()
                cons_fallback = self.ai_manager.consumption.is_using_fallback()
                
                if solar_fallback and cons_fallback:
                    logger.info("⚠️  AI models using fallback (simulation mode)")
                    self.use_ai = False  # Disable AI if both models failed
                elif not solar_fallback and not cons_fallback:
                    logger.info("✅ AI models active (94% solar, 53% consumption accuracy)")
                else:
                    if solar_fallback:
                        logger.info("⚠️  Solar model using fallback")
                    if cons_fallback:
                        logger.info("⚠️  Consumption model using fallback")
            except Exception as e:
                logger.warning(f"Failed to initialize AI models: {e}, using simulation")
                self.use_ai = False
                self.ai_manager = None
    
    def generate_24h_environment(self) -> List[EnvironmentState]:
        """Generate 24 hours of environment data.
        
        Uses AI models if available, otherwise falls back to simulation.
        
        Returns:
            List of EnvironmentState (one per hour)
        """
        return [self._generate_hour(hour) for hour in range(24)]
    
    def _generate_hour(self, hour: int) -> EnvironmentState:
        """Generate environment data for a single hour.
        
        Args:
            hour: Hour of day (0-23)
            
        Returns:
            EnvironmentState with solar, load, and price
        """
        solar = self._generate_solar_for_hour(hour)
        load = self._generate_consumption_for_hour(hour)
        price = get_price_for_hour(hour)
        
        return EnvironmentState(
            hour=hour,
            solar_kwh=solar,
            load_kwh=load,
            price=price
        )
    
    def generate_environment_for_hour(self, hour: int) -> EnvironmentState:
        """Public method to generate environment for a specific hour.
        
        Used by AI model fallback system.
        
        Args:
            hour: Hour of day (0-23)
            
        Returns:
            EnvironmentState
        """
        return self._generate_hour(hour)
    
    def _generate_solar_for_hour(self, hour: int) -> float:
        """Generate solar production for a specific hour.
        
        Uses AI model if available, otherwise uses simulation.
        
        Args:
            hour: Hour of day (0-23)
            
        Returns:
            Solar production in kWh
        """
        # Try AI model first
        if self.use_ai and self.ai_manager:
            try:
                # Get current date info (use defaults if not available)
                day = 15  # Middle of month
                month = 6 if self.config.season == Season.SUMMER else 12  # June or December
                weather_str = self.config.weather.value
                season_str = self.config.season.value
                
                # Get AI prediction
                solar_pred = self.ai_manager.solar.predict(
                    hour=hour,
                    day=day,
                    month=month,
                    weather=weather_str,
                    season=season_str
                )
                
                # Validate prediction (should be 0-10 kW range)
                if 0 <= solar_pred <= 15:
                    return solar_pred
                else:
                    logger.warning(f"AI solar prediction out of range: {solar_pred}, using simulation")
                    
            except Exception as e:
                logger.debug(f"AI solar prediction failed for hour {hour}: {e}")
        
        # Fallback to simulation
        return self._generate_solar_simulation(hour)
    
    def _generate_solar_simulation(self, hour: int) -> float:
        """Original solar simulation (fallback method).
        
        Args:
            hour: Hour of day (0-23)
            
        Returns:
            Solar production in kWh
        """
        # No solar at night
        if hour < 6 or hour > 18:
            return 0.0
        
        # Determine peak based on season
        peak = SOLAR_SUMMER_PEAK if self.config.season == Season.SUMMER else SOLAR_WINTER_PEAK
        
        # Apply weather multiplier
        weather_mult = WEATHER_MULTIPLIERS.get(self.config.weather.value, 1.0)
        
        # Generate bell curve for solar production
        # Peak at 12:00-13:00
        if 6 <= hour <= 12:
            # Morning ramp up
            progress = (hour - 6) / 6
            base = peak * np.sin(progress * np.pi / 2)
        elif 12 < hour <= 14:
            # Peak hours
            base = peak
        elif 14 < hour <= 18:
            # Afternoon ramp down
            progress = (18 - hour) / 4
            base = peak * np.sin(progress * np.pi / 2)
        else:
            return 0.0
        
        # Add random variation (±15%) and weather
        variation = 0.7 + 0.3 * self.rng.random()
        solar = base * variation * weather_mult
        
        # Apply inverter limit
        solar = min(solar, INVERTER_MAX_OUTPUT)
        
        return solar
    
    def _generate_consumption_for_hour(self, hour: int) -> float:
        """Generate consumption for a specific hour.
        
        Uses AI model if available, otherwise uses simulation.
        
        Args:
            hour: Hour of day (0-23)
            
        Returns:
            Consumption in kWh
        """
        # Try AI model first
        if self.use_ai and self.ai_manager:
            try:
                # Get current date info
                day = 15  # Middle of month
                month = 6 if self.config.season == Season.SUMMER else 12
                weather_str = self.config.weather.value
                season_str = self.config.season.value
                
                # Get AI prediction
                cons_pred = self.ai_manager.consumption.predict(
                    hour=hour,
                    day=day,
                    month=month,
                    weather=weather_str,
                    season=season_str
                )
                
                # Validate prediction (should be 0-10 kW range for household)
                if 0 <= cons_pred <= 10:
                    return cons_pred
                else:
                    logger.warning(f"AI consumption prediction out of range: {cons_pred}, using simulation")
                    
            except Exception as e:
                logger.debug(f"AI consumption prediction failed for hour {hour}: {e}")
        
        # Fallback to simulation
        return self._generate_consumption_simulation(hour)
    
    def _generate_consumption_simulation(self, hour: int) -> float:
        """Original consumption simulation (fallback method).
        
        Args:
            hour: Hour of day (0-23)
            
        Returns:
            Consumption in kWh
        """
        # Get base consumption for time period
        period = get_consumption_period(hour)
        if self.config.day_type.value == "weekend":
            base = CONSUMPTION_BASE_WEEKEND.get(period, 1.0)
        else:
            base = CONSUMPTION_BASE_WEEKDAY.get(period, 1.0)
        
        # Apply season multiplier
        season_mult = SEASON_MULTIPLIERS.get(self.config.season.value, 1.0)
        base = base * season_mult
        
        # Add random variation (±15%) using reproducible RNG
        variation = self.rng.uniform(0.85, 1.15)
        
        return base * variation
    
    def get_ai_status(self) -> dict:
        """Get status of AI models.
        
        Returns:
            Dictionary with AI status information
        """
        if self.ai_manager:
            return self.ai_manager.get_model_status()
        else:
            return {
                'solar': {'loaded': False, 'using_fallback': True, 'accuracy': 0},
                'consumption': {'loaded': False, 'using_fallback': True, 'accuracy': 0}
            }
    
    def generate_24h_data(self):
        """DEPRECATED: Use SimulationRunner instead.
        
        Kept for backward compatibility during migration.
        Will be removed in future version.
        """
        raise NotImplementedError(
            "EnergyDataSimulator no longer runs full simulation. "
            "Use SimulationRunner for complete simulation. "
            "Or call generate_24h_environment() for environment data only."
        )
