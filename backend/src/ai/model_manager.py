"""
Model Manager - Central access to both AI models (solar and consumption).
Provides unified interface for predictions with fallback support.

SINGLETON PATTERN: Models load only once, reused for all requests.
"""
import datetime
import logging
from typing import Dict, Any, Optional

from .solar_predictor import SolarPredictor
from .consumption_predictor import ConsumptionPredictor

logger = logging.getLogger(__name__)


class ModelManager:
    """
    Central manager for all AI prediction models.
    Provides easy access to both solar and consumption predictions.
    
    SINGLETON PATTERN: This class uses the singleton pattern to ensure
    AI models are loaded only once and reused for all predictions.
    This prevents the 29MB model files from being reloaded on every request.
    
    Usage:
        manager = ModelManager()  # Loads models on first call
        manager = ModelManager()  # Returns same instance, no reload
    """
    
    # Singleton instance storage
    _instance: Optional['ModelManager'] = None
    _initialized: bool = False
    
    def __new__(cls) -> 'ModelManager':
        """Create or return singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize both AI models (only once)."""
        # Skip initialization if already done (singleton pattern)
        if self._initialized:
            return
        
        logger.info("🔄 Initializing AI Model Manager (singleton)...")
        
        self.solar = SolarPredictor()
        self.consumption = ConsumptionPredictor()
        
        # Log status
        solar_fallback = self.solar.is_using_fallback()
        cons_fallback = self.consumption.is_using_fallback()
        
        if not solar_fallback and not cons_fallback:
            logger.info("✅ All AI models loaded successfully (singleton)")
        elif solar_fallback and cons_fallback:
            logger.warning("⚠️  Both models using fallback (simulation mode)")
        else:
            if solar_fallback:
                logger.warning("⚠️  Solar model using fallback")
            if cons_fallback:
                logger.warning("⚠️  Consumption model using fallback")
        
        # Mark as initialized to prevent reloading
        self._initialized = True
        logger.info("🔒 ModelManager singleton initialized - models will NOT reload on subsequent requests")
    
    @classmethod
    def reset_instance(cls):
        """Reset singleton (mainly for testing)."""
        cls._instance = None
        cls._initialized = False
        logger.info("🔄 ModelManager singleton reset")
    
    def get_predictions(self, 
                       hour: int = None,
                       day: int = None,
                       month: int = None,
                       year: int = None,
                       weather: str = 'sunny',
                       season: str = 'summer') -> Dict[str, Any]:
        """
        Get both solar and consumption predictions for a specific time.
        
        Args:
            hour: Hour of day (0-23). If None, uses current hour.
            day: Day of month (1-31). If None, uses current day.
            month: Month (1-12). If None, uses current month.
            year: Year (e.g., 2024). If None, uses current year.
            weather: Weather condition ('sunny', 'partly_cloudy', 'cloudy', 'rainy')
            season: Season ('summer', 'winter')
            
        Returns:
            Dictionary containing:
            - solar_kw: Predicted solar production (kW)
            - consumption_kw: Predicted consumption (kW)
            - net_kw: Net energy (solar - consumption)
            - solar_accuracy: Solar model accuracy
            - consumption_accuracy: Consumption model accuracy
            - using_fallback: Whether fallback mode is active
            - timestamp: Prediction timestamp
            - input_params: Input parameters used
        """
        # Get current time if not specified
        now = datetime.datetime.now()
        hour = hour if hour is not None else now.hour
        day = day if day is not None else now.day
        month = month if month is not None else now.month
        year = year if year is not None else now.year
        
        # Get predictions from both models
        solar_pred = self.solar.predict(hour, day, month, weather, season)
        consumption_pred = self.consumption.predict(hour, day, month, weather=weather, season=season)
        
        # Calculate net
        net = solar_pred - consumption_pred
        
        # Check if using fallback
        using_fallback = self.solar.is_using_fallback() or self.consumption.is_using_fallback()
        
        return {
            'solar_kw': solar_pred,
            'consumption_kw': consumption_pred,
            'net_kw': net,
            'solar_accuracy': self.solar.ACCURACY,
            'consumption_accuracy': self.consumption.ACCURACY,
            'using_fallback': using_fallback,
            'timestamp': now.isoformat(),
            'input_params': {
                'hour': hour,
                'day': day,
                'month': month,
                'year': year,
                'weather': weather,
                'season': season
            }
        }
    
    def get_24h_predictions(self, 
                            day: int = None,
                            month: int = None,
                            year: int = None,
                            weather: str = 'sunny',
                            season: str = 'summer') -> list:
        """
        Get predictions for all 24 hours of a day.
        
        Args:
            day: Day of month (1-31)
            month: Month (1-12)
            year: Year (e.g., 2024)
            weather: Weather condition
            season: Season
            
        Returns:
            List of 24 prediction dictionaries (one per hour)
        """
        now = datetime.datetime.now()
        day = day if day is not None else now.day
        month = month if month is not None else now.month
        year = year if year is not None else now.year
        
        predictions = []
        for hour in range(24):
            pred = self.get_predictions(
                hour=hour,
                day=day,
                month=month,
                year=year,
                weather=weather,
                season=season
            )
            predictions.append(pred)
        
        return predictions
    
    def get_feature_importance(self) -> Dict[str, Dict[str, float]]:
        """
        Get feature importance from both models.
        
        Returns:
            Dictionary with feature importance for both models
        """
        return {
            'solar': self.solar.get_feature_importance(),
            'consumption': self.consumption.get_feature_importance()
        }
    
    def get_model_status(self) -> Dict[str, Any]:
        """
        Get status of both models.
        
        Returns:
            Dictionary with model status information
        """
        return {
            'solar': {
                'loaded': self.solar.model is not None,
                'using_fallback': self.solar.is_using_fallback(),
                'accuracy': self.solar.ACCURACY
            },
            'consumption': {
                'loaded': self.consumption.model is not None,
                'using_fallback': self.consumption.is_using_fallback(),
                'accuracy': self.consumption.ACCURACY
            },
            'singleton_initialized': self._initialized
        }
