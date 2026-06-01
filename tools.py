import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Simple mapping (can expand later)
CITY_COORDS = {
    "bangalore": (12.97, 77.59),
    "delhi": (28.61, 77.20),
    "mumbai": (19.07, 72.87)
}


def get_air_quality(city="bangalore"):
    city = city.lower()

    lat, lon = CITY_COORDS.get(city, (12.97, 77.59))  # default Bangalore

    url = "https://air-quality-api.open-meteo.com/v1/air-quality"

    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "pm10,pm2_5"
    }

    response = requests.get(url, params=params, verify=False)
    data = response.json()

    pm10 = data["hourly"]["pm10"][0]
    pm25 = data["hourly"]["pm2_5"][0]

    return {
        "city": city,
        "pm10": pm10,
        "pm2_5": pm25
    }