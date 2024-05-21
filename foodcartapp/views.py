from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.templatetags.static import static
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from phonenumbers import is_valid_number, parse
from phonenumbers.phonenumberutil import NumberParseException

from .models import Product, Order, OrderProduct


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


@api_view(['POST'])
def register_order(request):
    required_fields = {
        'products': list,
        'firstname': str,
        'lastname': str,
        'phonenumber': str,
        'address': str
    }
    order = request.data
    error_msg = {}

    for field_name, field_type in required_fields.items():
        if field_name not in order:
            error_msg['error'] = f'{field_name} key is missing.'
            return Response(error_msg, status=status.HTTP_406_NOT_ACCEPTABLE)
        elif not isinstance(order[field_name], field_type):
            error_msg['error'] = f'{field_name} is not {field_type}'
            return Response(error_msg, status=status.HTTP_406_NOT_ACCEPTABLE)
        elif not order[field_name]:
            error_msg['error'] = f'{field_name} is empty.'
            return Response(error_msg, status=status.HTTP_406_NOT_ACCEPTABLE)

    products = order['products']
    for product in products:
        try:
            Product.objects.get(pk=product['product'])
        except Product.DoesNotExist:
            error_msg['error'] = f'Product with id {product["product"]} does not exists.'
            return Response(error_msg, status=status.HTTP_406_NOT_ACCEPTABLE)

    try:
        parsed_number = parse(order['phonenumber'])
    except NumberParseException:
        error_msg['error'] = f'Phone number {order["phonenumber"]} is not valid.'
        return Response(error_msg, status=status.HTTP_406_NOT_ACCEPTABLE)

    if not is_valid_number(parsed_number):
        error_msg['error'] = f'Phone number {order["phonenumber"]} is not valid.'
        return Response(error_msg, status=status.HTTP_406_NOT_ACCEPTABLE)

    db_order = Order.objects.create(
        first_name=order['firstname'],
        last_name=order['lastname'],
        phone_number=order['phonenumber'],
        address=order['address'],
    )

    for order_product in order['products']:
        OrderProduct.objects.create(
            order=db_order,
            product=get_object_or_404(
                Product,
                pk=order_product['product']
            ),
            amount=order_product['quantity']
        )

    return Response({})
