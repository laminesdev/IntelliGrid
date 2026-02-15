"""
AI Solar Predictor - Uses trained PVGIS model for solar production prediction.
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


class SolarPredictor:
    """
    AI-powered solar production predictor using trained PVGIS model.
    Falls back to simulation if model fails to load or predict.
    """
    
    # Model accuracy from training
    ACCURACY = 0.94
    
    # Weather to GHI mapping (W/m²)
    WEATHER_TO_GHI = {
        'sunny': 800,
        'partly_cloudy': 500,
        'cloudy': 200,
        'rainy': 100,
        'partly_cloudy': 500,  # Handle underscore version
        'cloudy': 200,
        'rainy': 100,
    }
    
    # Weather to temperature mapping (°C)
    WEATHER_TO_TEMP = {
        'sunny': 32,
        'partly_cloudy': 28,
        'cloudy': 22,
        'rainy': 18,
        'partly_cloudy': 28,
        'cloudy': 22,
        'rainy': 18,
    }
    
    # Season to temperature adjustment
    SEASON_TO_TEMP = {
        'summer': 35,
        'winter': 12,
    }
    
    def __init__(self, model_path=None):
        """
        Initialize the solar predictor.
        
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
            model_path = backend_dir / "models" / "solar_pv_model.pkl"
        else:
            model_path = Path(model_path)
        
        # Try to load the model
        if ML_AVAILABLE:
            try:
                self.model = joblib.load(model_path)
                logger.info(f"✅ Solar model loaded successfully from {model_path}")
                logger.info(f"   Model accuracy: {self.ACCURACY:.1%}")
            except Exception as e:
                logger.warning(f"⚠️  Failed to load solar model: {e}")
                logger.warning("   Using simulation fallback")
                self.using_fallback = True
        else:
            logger.warning("⚠️  ML libraries not available, using simulation fallback")
            self.using_fallback = True
    
    def predict(self, hour, day, month, weather='sunny', season='summer'):
        """
        Predict solar production in kW.
        
        Args:
            hour: Hour of day (0-23)
            day: Day of month (1-31)
            month: Month (1-12)
            weather: Weather condition ('sunny', 'partly_cloudy', 'cloudy', 'rainy')
            season: Season ('summer', 'winter')
            
        Returns:
            Predicted solar production in kW (float)
        """
        # Map weather to GHI and temperature
        ghi = self.WEATHER_TO_GHI.get(weather.lower().replace('-', '_'), 500)
        temp = self.WEATHER_TO_TEMP.get(weather.lower().replace('-', '_'), 25)
        
        # Adjust temperature by season
        if season.lower() == 'summer':
            temp = max(temp, 30)
        elif season.lower() == 'winter':
            temp = min(temp, 15)
        
        # Try AI model first
        if self.model is not None and not self.using_fallback:
            try:
                # Prepare features (must match training features)
                features = pd.DataFrame([{
                    'Hour': hour,
                    'Day': day,
                    'Month': month,
                    'G(i)': ghi,
                    'T2m': temp
                }])
                
                # Make prediction
                pred_watts = self.model.predict(features)[0]
                
                # Convert W to kW and ensure non-negative
                pred_kw_raw = max(0, pred_watts / 1000)
                
                # SCALE FIX: Model outputs ~250W peak, should be ~10kW (40x scale)
                # The model was trained on normalized/percentage data
                SCALE_FACTOR = 40.0
                pred_kw = pred_kw_raw * SCALE_FACTOR
                
                return pred_kw
                
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
        
        return env.solar_kwh
    
    def get_feature_importance(self):
        """
        Get feature importance from model training.
        
        Returns:
            Dictionary of feature importance scores
        """
        return {
            'G(i) - Solar Radiation': 0.79,
            'Hour': 0.12,
            'T2m - Temperature': 0.06,
            'Day': 0.02,
            'Month': 0.01
        }
    
    def is_using_fallback(self):
        """
        Check if predictor is using fallback mode.
        
        Returns:
            Boolean indicating fallback status
        """
        return self.using_fallback
