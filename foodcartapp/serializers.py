from rest_framework.serializers import ModelSerializer
from requests.exceptions import HTTPError, ConnectionError

from .models import Order, OrderProduct
from places.geocoder import fetch_coordinates, create_place
from star_burger.settings import YANDEX_GEOCODER_KEY


class OrderProductSerializer(ModelSerializer):
    class Meta:
        model = OrderProduct
        fields = ('product', 'quantity')


class OrderSerializer(ModelSerializer):
    products = OrderProductSerializer(
        many=True,
        allow_empty=False,
        write_only=True
    )

    class Meta:
        model = Order
        fields = (
            'id',
            'firstname',
            'lastname',
            'phonenumber',
            'address',
            'products'
        )

    def create(self, validated_data):
        order = Order.objects.create(
            firstname=validated_data['firstname'],
            lastname=validated_data['lastname'],
            phonenumber=validated_data['phonenumber'],
            address=validated_data['address'],
        )

        order_items = validated_data['products']
        for order_item in order_items:
            order_item['price'] = order_item['product'].price

        products = [
            OrderProduct(order=order, **fields) for fields in order_items
        ]

        OrderProduct.objects.bulk_create(products)

        try:
            fetched_coordinates = fetch_coordinates(
                YANDEX_GEOCODER_KEY, validated_data['address']
            )
        except (HTTPError, ConnectionError):
            fetched_coordinates = None

        if fetched_coordinates:
            order_coordinates = {
                'latitude': fetched_coordinates[0],
                'longitude': fetched_coordinates[1]
            }
        else:
            order_coordinates = None

        create_place(validated_data['address'], order_coordinates)

        return order
