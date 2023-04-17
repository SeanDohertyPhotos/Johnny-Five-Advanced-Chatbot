import requests

def get_weather(location):
    api_key = 'your_weather_api_key'
    base_url = 'http://api.openweathermap.org/data/2.5/weather'
    params = {
        'q': location,
        'appid': api_key,
        'units': 'metric'
    }
    response = requests.get(base_url, params=params)
    return response.json()
