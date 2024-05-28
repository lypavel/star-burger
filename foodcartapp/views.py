from django.db import transaction
from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status as st

from requests.exceptions import HTTPError, ConnectionError

from .models import Product, Order, OrderProduct
from .serializers import OrderSerializer
from places.geocoder import fetch_coordinates, create_place
from star_burger.settings import YANDEX_GEOCODER_KEY


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@transaction.atomic
@api_view(['POST'])
def register_order(request):

    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    validated_order = serializer.validated_data

    db_order = Order.objects.create(
        firstname=validated_order['firstname'],
        lastname=validated_order['lastname'],
        phonenumber=validated_order['phonenumber'],
        address=validated_order['address'],
    )

    order_items = validated_order['products']
    for order_item in order_items:
        order_item['price'] = order_item['product'].price

    products = [
        OrderProduct(order=db_order, **fields) for fields in order_items
    ]

    OrderProduct.objects.bulk_create(products)

    try:
        fetched_coordinates = fetch_coordinates(
            YANDEX_GEOCODER_KEY, validated_order['address']
        )
    except (HTTPError, ConnectionError):
        fetched_coordinates = None

    if fetched_coordinates:
        order_coordinates = {
            'latitude': fetched_coordinates[0],
            'longtitude': fetched_coordinates[1]
        }

    create_place(validated_order['address'], order_coordinates)

    return Response(OrderSerializer(db_order).data, status=st.HTTP_201_CREATED)
