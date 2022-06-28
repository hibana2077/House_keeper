'''
Author: error: git config user.name && git config user.email & please set dead value or install git
Date: 2022-06-28 18:40:43
LastEditors: error: git config user.name && git config user.email & please set dead value or install git
LastEditTime: 2022-06-28 22:11:06
FilePath: \summer project\info\weather.py
Description: weather.py
'''
#support by github Deactivate Copilot
import requests
from passwd import OPENWEATHER_API_KEY

def get_weather(city,OPENWEATHER_API_KEY):
    lat,lon = geocoding(city,OPENWEATHER_API_KEY)
    url = 'http://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid={}'.format(lat,lon,OPENWEATHER_API_KEY)
    r = requests.get(url)
    return dict(r.json())

def geocoding(city,OPENWEATHER_API_KEY):
    url = 'http://api.openweathermap.org/geo/1.0/direct?q={}&appid={}'.format(city, OPENWEATHER_API_KEY)
    r = requests.get(url)
    lat = r.json()[0]['lat']
    lon = r.json()[0]['lon']
    return lat,lon

def kelvin_to_celsius(kelvin):
    return round(kelvin - 273.15,2)

def air_pollution(city,OPENWEATHER_API_KEY):
    lat,lon = geocoding(city,OPENWEATHER_API_KEY)
    url = 'http://api.openweathermap.org/pollution/v1/city?lat={}&lon={}&appid={}'.format(lat,lon, OPENWEATHER_API_KEY)
    r = requests.get(url)
    return dict(r.json())

'''
how to use: get temperature in city:
北京 = 'beijing'
print(kelvin_to_celsius(get_weather(北京,OPENWEATHER_API_KEY)['main']['temp']))
'''

'''
get_weather returns a dict:
{
  "coord": {
    "lon": -122.08, # longitude
    "lat": 37.39    # latitude
  },
  "weather": [
    {
      "id": 800,
      "main": "Clear", # weather condition
      "description": "clear sky",# weather condition description
      "icon": "01d"
    }
  ],
  "base": "stations",
  "main": {
    "temp": 282.55, # temperature in Kelvin
    "feels_like": 281.86, # feels like temperature in Kelvin
    "temp_min": 280.37,
    "temp_max": 284.26,
    "pressure": 1023, # atmospheric pressure in hPa
    "humidity": 100 # humidity in %
  },
  "visibility": 10000, # visibility in meters you can change it to miles by dividing it by 1609.34
  "wind": {
    "speed": 1.5, # wind speed in m/s
    "deg": 350 # wind direction in degrees
  },
  "clouds": { # cloudiness in % (0-100)
    "all": 1
  },
  "dt": 1560350645, # time of data calculation in unix format unix time UTC
  "sys": {
    "type": 1,
    "id": 5122,
    "message": 0.0139,
    "country": "US", # country code
    "sunrise": 1560343627, # sunrise time in unix format unix time UTC
    "sunset": 1560396563 # sunset time in unix format unix time UTC
  },
  "timezone": -25200,
  "id": 420006353,
  "name": "Mountain View",
  "cod": 200
  }                                         
'''

'''
how to use: get air pollution in city:

returns a dict:
北京 = 'beijing'
print(kelvin_to_celsius(get_weather(北京,OPENWEATHER_API_KEY)['main']['temp'])) 

{
  "coord": [ # coordinates of the city
    50.0,
    50.0
  ],
  "list": [
    {
      "dt": 1606147200, # time of data calculation in unix format unix time UTC
      "main": {
        "aqi": 4.0 # air quality index 1 for good, 2 for fair , 3 for moderate, 4 for bad, 5 for very bad
      },
      "components": {
        "co": 203.609, # carbon monoxide in parts per billion
        "no": 0.0, # nitrogen dioxide monoxide in parts per billion 
        "no2": 0.396, # nitrogen dioxide in parts per billion
        "o3": 75.102,  # ozone in parts per billion
        "so2": 0.648, # sulfur dioxide in parts per billion
        "pm2_5": 23.253, # particulate matter 2.5 in parts per billion
        "pm10": 92.214, # particulate matter 10 in parts per billion
        "nh3": 0.117 # Ammonia in parts per billion
      }
    }
  ]
}
'''