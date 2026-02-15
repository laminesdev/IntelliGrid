"""
AI Consumption Predictor - Uses trained household power consumption model.
Provides fallback to simulation if model fails.
"""
import sys
from pathlib import Path
import logging

# Setup logging
logger = logging.getLogger(__name__)

# Try to import ML libraries
try:
    import joblib
    import pandas as pd
    import numpy as np
    ML_AVAILABLE = True
except ImportError as e:
    logger.warning(f"ML libraries not available: {e}")
    ML_AVAILABLE = False

# Import fallback simulator
from src.data.simulator import EnergyDataSimulator


class ConsumptionPredictor:
    """
    AI-powered consumption predictor using trained time-power model.
    Falls back to simulation if model fails to load or predict.
    """
    
    # Model accuracy from training
    ACCURACY = 0.53
    
    def __init__(self, model_path=None):
        """
        Initialize the consumption predictor.
        
        Args:
            model_path: Path to .pkl model file. If None, uses default path.
        """
        self.model = None
        self.using_fallback = False
        
        # Set default model path
        if model_path is None:
            # Navigate from src/ai/ to backend/models/
            current_file = Path(__file__).resolve()
            backend_dir = current_file.parent.parent.parent
            model_path = backend_dir / "models" / "time_power_model.pkl"
        else:
            model_path = Path(model_path)
        
        # Try to load the model
        if ML_AVAILABLE:
            try:
                self.model = joblib.load(model_path)
                logger.info(f"✅ Consumption model loaded successfully from {model_path}")
                logger.info(f"   Model accuracy: {self.ACCURACY:.1%}")
            except Exception as e:
                logger.warning(f"⚠️  Failed to load consumption model: {e}")
                logger.warning("   Using simulation fallback")
                self.using_fallback = True
        else:
            logger.warning("⚠️  ML libraries not available, using simulation fallback")
            self.using_fallback = True
    
    def predict(self, hour, day, month, dayofweek=None, weekend=None, weather='sunny', season='summer'):
        """
        Predict power consumption in kW.
        
        Args:
            hour: Hour of day (0-23)
            day: Day of month (1-31)
            month: Month (1-12)
            dayofweek: Day of week (0=Monday, 6=Sunday). If None, calculated from day/month.
            weekend: Whether it's weekend (0 or 1). If None, calculated from dayofweek.
            weather: Weather condition (for fallback)
            season: Season (for fallback)
            
        Returns:
            Predicted consumption in kW (float)
        """
        # Calculate dayofweek and weekend if not provided
        if dayofweek is None or weekend is None:
            try:
                import datetime
                date = datetime.date(2024, month, day)  # Use 2024 as default year
                if dayofweek is None:
                    dayofweek = date.weekday()  # 0=Monday, 6=Sunday
                if weekend is None:
                    weekend = 1 if dayofweek >= 5 else 0  # 5=Saturday, 6=Sunday
            except:
                # Default to weekday if calculation fails
                if dayofweek is None:
                    dayofweek = 0
                if weekend is None:
                    weekend = 0
        
        # Try AI model first
        if self.model is not None and not self.using_fallback:
            try:
                # Prepare features (must match training features)
                features = pd.DataFrame([{
                    'Hour': hour,
                    'Day': day,
                    'Month': month,
                    'DayOfWeek': dayofweek,
                    'Weekend': weekend
                }])
                
                # Make prediction
                pred_kw = self.model.predict(features)[0]
                
                # Ensure non-negative
                return max(0, pred_kw)
                
            except Exception as e:
                logger.error(f"AI prediction failed: {e}, using fallback")
                return self._fallback_predict(hour, day, month, weather, season)
        else:
            # Use fallback simulation
            return self._fallback_predict(hour, day, month, weather, season)
    
    def _fallback_predict(self, hour, day, month, weather, season):
        """
        Fallback to simulation-based prediction.
        """
        from src.data.models import SimulationConfig, Weather, Season, DayType
        
        # Create config for simulator
        weather_map = {
            'sunny': Weather.SUNNY,
            'partly_cloudy': Weather.PARTLY_CLOUDY,
            'cloudy': Weather.CLOUDY,
            'rainy': Weather.RAINY,
        }
        season_map = {
            'summer': Season.SUMMER,
            'winter': Season.WINTER,
        }
        
        config = SimulationConfig(
            season=season_map.get(season.lower(), Season.SUMMER),
            weather=weather_map.get(weather.lower().replace('-', '_'), Weather.SUNNY),
            day_type=DayType.WEEKDAY
        )
        
        # Create simulator and generate environment for specific hour
        simulator = EnergyDataSimulator(config, seed=42)
        env = simulator.generate_environment_for_hour(hour)
        
        return env.load_kwh
    
    def get_feature_importance(self):
        """
        Get feature importance from model training.
        
        Returns:
            Dictionary of feature importance scores
        """
        return {
            'Hour': 0.37,
            'Day': 0.28,
            'Month': 0.19,
            'DayOfWeek': 0.13,
            'Weekend': 0.02
        }
    
    def is_using_fallback(self):
        """
        Check if predictor is using fallback mode.
        
        Returns:
            Boolean indicating fallback status
        """
        return self.using_fallback
