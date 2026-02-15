"""
Weather alert routes.
"""
from fastapi import APIRouter, HTTPException
import traceback

from app.models import WeatherAlertRequest, WeatherAlertResponse, Alert
from app.models import Weather as WeatherEnum
from src.engine.weather_predictor import WeatherPredictor
from src.core.battery import Battery, BatteryState
from app.logging_config import logger

router = APIRouter()


@router.post("/weather/alerts", response_model=WeatherAlertResponse)
async def get_weather_alerts(request: WeatherAlertRequest):
    """
    Get weather-based alerts and recommendations.
    
    Analyzes current battery state and tomorrow's weather forecast to provide
    intelligent energy usage recommendations.
    
    Args:
        request: WeatherAlertRequest with battery SOC and weather forecast
        
    Returns:
        List of alerts with recommendations
    """
    try:
        # Convert weather enum
        weather_map = {
            WeatherEnum.SUNNY: 'sunny',
            WeatherEnum.PARTLY_CLOUDY: 'partly_cloudy',
            WeatherEnum.CLOUDY: 'cloudy',
            WeatherEnum.RAINY: 'rainy'
        }
        
        tomorrow_weather = None
        if request.tomorrow_weather:
            from src.data.models import Weather as CoreWeather
            core_weather_map = {
                WeatherEnum.SUNNY: CoreWeather.SUNNY,
                WeatherEnum.PARTLY_CLOUDY: CoreWeather.PARTLY_CLOUDY,
                WeatherEnum.CLOUDY: CoreWeather.CLOUDY,
                WeatherEnum.RAINY: CoreWeather.RAINY
            }
            tomorrow_weather = core_weather_map.get(request.tomorrow_weather)
        
        # Create battery state
        battery = Battery(13.5, initial_soc=request.battery_soc)
        
        # Get alerts
        predictor = WeatherPredictor(
            tomorrow_weather=tomorrow_weather,
            battery_state=battery.state,
            current_hour=request.current_hour
        )
        
        core_alerts = predictor.generate_alerts()
        
        # Convert to API model
        alerts = [
            Alert(
                type=alert.type,
                message=alert.message,
                priority=alert.priority,
                recommendation=alert.recommendation,
                icon=alert.icon
            )
            for alert in core_alerts
        ]
        
        status = predictor.get_current_status()
        
        return WeatherAlertResponse(
            alerts=alerts,
            status=status
        )
        
    except Exception as e:
        logger.error(f"Error in weather alerts: {e}")
        logger.debug(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/weather/alerts/test")
async def test_weather_alerts():
    """Test endpoint with sample data."""
    request = WeatherAlertRequest(
        tomorrow_weather=WeatherEnum.CLOUDY,
        battery_soc=0.25,
        current_hour=21
    )
    return await get_weather_alerts(request)
