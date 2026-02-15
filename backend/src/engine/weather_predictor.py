"""
Weather Predictor for generating alerts and recommendations.
"""
from typing import List, Optional
from src.data.models import Alert, Weather
from src.core.battery import BatteryState
from src.utils.config import BATTERY_MIN_SOC
# Icon identifiers for frontend (using Lucide icon names)


class WeatherPredictor:
    """Generates weather-based alerts and energy recommendations.
    
    Analyzes current battery state and tomorrow's forecast to provide
    intelligent energy usage recommendations.
    """
    
    def __init__(
        self,
        tomorrow_weather: Optional[Weather],
        battery_state: BatteryState,
        current_hour: int = 20
    ):
        """Initialize weather predictor.
        
        Args:
            tomorrow_weather: Weather forecast for tomorrow
            battery_state: Current battery state
            current_hour: Current hour (default 20:00 for evening planning)
        """
        self.tomorrow_weather = tomorrow_weather
        self.battery_state = battery_state
        self.current_hour = current_hour
        
    @property
    def current_battery_soc(self) -> float:
        """Get current battery SOC for backward compatibility."""
        return self.battery_state.soc
        
    def generate_alerts(self) -> List[Alert]:
        """Generate list of weather-based alerts and recommendations.
        
        Returns:
            List of Alert objects with priority ordering
        """
        alerts = []
        
        # Check if we have forecast data
        if self.tomorrow_weather is None:
            return alerts
        
        # Critical battery + cloudy tomorrow
        if (self.current_battery_soc < BATTERY_MIN_SOC + 0.10 and 
            self.tomorrow_weather in [Weather.CLOUDY, Weather.RAINY]):
            alerts.append(Alert(
                type="danger",
                message="Critical Battery Alert",
                priority=1,
                recommendation="Battery below 30% with poor weather forecasted. "
                            "Minimize non-essential usage tonight. Consider charging from grid if rates are low.",
                icon="alert-circle"
            ))
        
        # Low battery + cloudy tomorrow
        elif (self.current_battery_soc < 0.40 and 
              self.tomorrow_weather in [Weather.CLOUDY, Weather.RAINY]):
            alerts.append(Alert(
                type="warning",
                message="Conservation Mode Recommended",
                priority=2,
                recommendation="Cloudy weather forecasted tomorrow with battery at {}%. "
                            "Delay heavy appliance usage until after tomorrow afternoon.".format(
                                int(self.current_battery_soc * 100)
                            ),
                icon="cloud"
            ))
        
        # Sunny tomorrow + high battery
        elif (self.tomorrow_weather == Weather.SUNNY and 
              self.current_battery_soc > 0.80):
            alerts.append(Alert(
                type="success",
                message="Optimal Conditions Tomorrow",
                priority=3,
                recommendation="Sunny weather forecasted with full battery reserve. "
                            "Ideal day for energy-intensive activities like laundry or EV charging.",
                icon="sun"
            ))
        
        # Partly cloudy + moderate battery
        elif (self.tomorrow_weather == Weather.PARTLY_CLOUDY and 
              0.40 <= self.current_battery_soc <= 0.70):
            alerts.append(Alert(
                type="info",
                message="Balanced Energy Day Expected",
                priority=4,
                recommendation="Moderate solar production forecasted. "
                            "Standard usage patterns recommended. Battery at optimal level.",
                icon="cloud-sun"
            ))
        
        # Rainy tomorrow + any battery level
        elif self.tomorrow_weather == Weather.RAINY:
            alerts.append(Alert(
                type="warning",
                message="Rainy Weather Ahead",
                priority=3,
                recommendation="Minimal solar production expected tomorrow. "
                            "Conserve battery tonight. Heavy usage will require grid power.",
                icon="cloud-rain"
            ))
        
        # Evening time + low battery (regardless of tomorrow's weather)
        if self.current_hour >= 21 and self.current_battery_soc < 0.25:
            alerts.append(Alert(
                type="warning",
                message="Evening Battery Low",
                priority=2,
                recommendation="Battery critically low for overnight. "
                            "Postpone non-essential usage until morning.",
                icon="moon"
            ))
        
        # Sort by priority
        alerts.sort(key=lambda x: x.priority)
        
        return alerts
    
    def get_current_status(self) -> str:
        """Get a summary of current battery and weather status.
        
        Returns:
            Status message string
        """
        soc_percent = int(self.current_battery_soc * 100)
        
        if self.tomorrow_weather:
            weather_desc = self.tomorrow_weather.value.replace("_", " ").title()
            return f"Battery: {soc_percent}% | Tomorrow: {weather_desc}"
        else:
            return f"Battery: {soc_percent}% | No forecast data"
    
    def should_delay_usage(self, appliance_type: str = "heavy") -> bool:
        """Determine if appliance usage should be delayed.
        
        Args:
            appliance_type: Type of appliance usage ("heavy" or "light")
            
        Returns:
            True if usage should be delayed
        """
        if self.tomorrow_weather is None:
            return False
        
        if appliance_type == "heavy":
            # Heavy appliances (dishwasher, washing machine, dryer, EV charging)
            if (self.tomorrow_weather in [Weather.CLOUDY, Weather.RAINY] and 
                self.current_battery_soc < 0.50):
                return True
            if self.tomorrow_weather == Weather.SUNNY and self.current_battery_soc > 0.70:
                return False
        
        return False