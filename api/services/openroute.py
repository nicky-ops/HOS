import requests
from django.conf import settings
import os
from dotenv import load_dotenv

load_dotenv()


class OpenRouteService:
    '''
    This class represents the OpenRouteService
    '''
    BASE_URL = os.get_env('OPENROUTE_BASE_URL')
    API_KEY = os.get_env('OPENROUTE_API_KEY')

    def __init__(self):
        self.api_key = self.API_KEY

    def get_route(self, start, pickup, dropoff):
        '''
        Get route data from OpenRouteService
        '''
        coordinates =[
            [start['lng'], start['lat']],
            [pickup['lng'], pickup['lat']],
            [dropoff['lng'], dropoff['lat']]
        ]

        payload = {
            "coordinates": coordinates,
            "instructions": True,
            "geometry": True,
            "preference": "recommended",
        }

        headers = {
            'Authorization': self.api_key
            'Content-Type': 'application/json'
        }

        response = requests.post(
            f"{self.BASE_URL}/directions/driving-car",
            headers=headers,
            json=payload
        )

        if response.status_code != 200:
            raise Exception(f"ORS API error: {response.text}")

        data = response.json()

        return {
            'distance': data['routes'][0]['summary']['distance'] / 1609.34, # Convert meters to miles
            'duration': data['routes'][0]['summary']['duration'] / 3600 # Convert seconds to hours
            'geometry': data['routes'][0]['geometry'],
            'instructions': data['routes'][0]['segments'][0]['steps']
        }

