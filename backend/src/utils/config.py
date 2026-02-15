"""
Configuration constants for IntelliGrid Energy Management System.
"""

# Battery Configuration
BATTERY_CAPACITY = 13.5          # kWh maximum capacity
BATTERY_EFFICIENCY = 0.92        # Round-trip efficiency (92%)
BATTERY_MAX_CHARGE_RATE = 5.0    # kW max charging rate
BATTERY_MAX_DISCHARGE_RATE = 5.0 # kW max discharging rate
BATTERY_MIN_SOC = 0.20          # Minimum state of charge (20%)
BATTERY_MAX_SOC = 0.95          # Maximum state of charge (95%)

# Inverter Configuration
INVERTER_MAX_OUTPUT = 8.0       # kW maximum output

# Solar Configuration
SOLAR_SUMMER_PEAK = 10.0        # kW peak production in summer
SOLAR_WINTER_PEAK = 5.0         # kW peak production in winter

# Weather Multipliers (solar production)
WEATHER_MULTIPLIERS = {
    "sunny": 1.0,
    "partly_cloudy": 0.7,
    "cloudy": 0.4,
    "rainy": 0.2
}

# Time-of-Use Pricing (DZD/kWh) - Algeria Sonelgaz rates 2025
# Based on GlobalPetrolPrices.com June 2025 data: Residential DZD 5.65/kWh
# Using smart grid simulation with peak/off-peak differentials
PRICING = {
    "peak": 6.78,      # 18:00-22:00 - Peak hours (20% premium)
    "normal": 5.65,    # 07:00-18:00, 22:00-23:00 - Standard rate  
    "night": 4.80      # 23:00-07:00 - Off-peak (15% discount)
}

# Grid export price when selling excess energy (net metering/feed-in)
# Algeria currently developing solar feed-in tariffs
GRID_EXPORT_PRICE = 4.00        # DZD/kWh (70% of retail rate)

# Consumption Patterns (base load in kW)
CONSUMPTION_BASE_WEEKDAY = {
    "night": 0.5,      # 23:00-07:00
    "morning": 2.5,    # 07:00-09:00
    "day": 1.0,        # 09:00-18:00
    "evening": 4.0     # 18:00-23:00
}

CONSUMPTION_BASE_WEEKEND = {
    "night": 0.6,
    "morning": 3.0,
    "day": 2.0,
    "evening": 3.5
}

# Season multipliers for consumption
SEASON_MULTIPLIERS = {
    "summer": 1.3,     # Higher AC usage
    "winter": 0.8      # Lower consumption
}

# Environmental Impact Factors - Algeria Context
# Algeria's grid is 99% natural gas (IEA 2022 data)
CO2_FACTOR = 0.55       # kg CO2 per kWh (natural gas + transmission losses)
TREES_PER_TON_CO2 = 50  # Trees needed to offset 1 ton CO2 per year

# Additional Environmental Factors
WATER_FACTOR = 1.5      # Liters of water saved per kWh (thermal cooling)
NOX_FACTOR = 0.0008     # kg NOx reduced per kWh
SO2_FACTOR = 0.0003     # kg SO2 reduced per kWh (minimal in gas plants)
PM10_FACTOR = 0.0002    # kg PM10 (particulate matter) reduced per kWh

# Transport equivalence factors
KM_PER_KG_CO2_CAR = 0.25    # km driven per kg CO2 (avg car: 0.25 kg CO2/km)
KM_PER_KG_CO2_BUS = 1.0     # km driven per kg CO2 (bus: more efficient)

# UI Colors
COLORS = {
    "primary": "#99E135",      # Main brand color
    "solar": "#FFD700",        # Solar production (gold)
    "battery": "#2E8B57",      # Battery (sea green)
    "consumption": "#FF6347",   # Consumption (coral)
    "grid": "#4169E1",         # Grid usage (royal blue)
    "success": "#28a745",
    "warning": "#ffc107", 
    "danger": "#dc3545"
}


def get_price_for_hour(hour: int) -> float:
    """Get electricity price for a specific hour."""
    if 18 <= hour < 22:
        return PRICING["peak"]
    elif hour >= 23 or hour < 7:
        return PRICING["night"]
    return PRICING["normal"]


def get_consumption_period(hour: int) -> str:
    """Determine consumption period based on hour."""
    if hour >= 23 or hour < 7:
        return "night"
    elif 7 <= hour < 9:
        return "morning"
    elif 9 <= hour < 18:
        return "day"
    else:
        return "evening"