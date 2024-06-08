from django.utils import timezone
import requests as rq

from .models import Place


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = rq.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lat, lon


def create_place(address, coordinates=None):
    if coordinates:
        latitude = coordinates['latitude']
        longtitude = coordinates['longtitude']
    else:
        latitude = longtitude = None

    place, _ = Place.objects.update_or_create(
        address=address,
        defaults={
            "latitude": latitude,
            "longtitude": longtitude,
            "updated_at": timezone.now()
        }
    )
