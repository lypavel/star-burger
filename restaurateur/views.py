from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from geopy import distance
import requests as rq

from foodcartapp.models import Product, Restaurant, Order, RestaurantMenuItem
from star_burger.settings import YANDEX_GEOCODER_KEY


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {item.restaurant_id: item.availability for item in product.menu_items.all()}
        ordered_availability = [availability.get(restaurant.id, False) for restaurant in restaurants]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurant_availability': products_with_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


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


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    orders = Order.objects\
        .exclude(status=Order.OrderStatus.finished)\
        .prefetch_related('products', 'restaurant')\
        .annotate(full_price=Order.objects.calculate_full_price())\
        .order_by('status', 'id')

    menu_items = RestaurantMenuItem.objects\
        .prefetch_related('product', 'restaurant')

    restaurants = Restaurant.objects.all()

    for order in orders:
        available_restaurants = {}

        order_coordinates = fetch_coordinates(YANDEX_GEOCODER_KEY, order.address)
        for order_product in order.products.select_related('product'):
            possible_restaurants = set(
                menu_items\
                    .filter(product=order_product.product)\
                    .values_list('restaurant', flat=True)
            )
            if not available_restaurants:
                available_restaurants = possible_restaurants
            else:
                available_restaurants.intersection_update(possible_restaurants)

        final_restaurants = []
        for restaurant in available_restaurants:
            restaurant_db = restaurants.get(pk=restaurant)
            restaurant_coordinates = fetch_coordinates(YANDEX_GEOCODER_KEY, restaurant_db.address)
            order_distance = None
            if restaurant_coordinates and order_coordinates:
                order_distance = distance.distance(
                    (order_coordinates),
                    (restaurant_coordinates)
                ).km

            if order_distance:
                order_distance = round(order_distance, 2)
            else:
                order_distance = 'Ошибка определения координат'

            final_restaurants.append(
                {
                    'name': restaurant_db.name,
                    'distance':  order_distance
                }
            )

        order.restaurants = sorted(
            final_restaurants,
            key=lambda restaurant: restaurant['distance']
        )

    return render(request, template_name='order_items.html', context={
        'order_items': orders
    })
