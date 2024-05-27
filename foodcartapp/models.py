from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum, F
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=400,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):
    def calculate_full_price(self):
        return Sum(
            F('products__price') * F('products__quantity')
        )


class Order(models.Model):
    class OrderStatus(models.TextChoices):
        created = ('1', 'Создан',)
        processed = ('2', 'Готовится',)
        delivering = ('3', 'Доставляется')
        finished = ('4', 'Завершён')

    class PaymentMethods(models.TextChoices):
        cash = ('Наличные', 'Наличные')
        card = ('Банковская карта', 'Банковская карта')

    firstname = models.CharField(
        max_length=100,
        verbose_name='Имя'
    )
    lastname = models.CharField(
        max_length=100,
        verbose_name='Фамилия'
    )
    phonenumber = PhoneNumberField(
        verbose_name='номер телефона',
        db_index=True
    )
    address = models.CharField(
        verbose_name='адрес',
        max_length=200
    )

    status = models.CharField(
        'статус',
        max_length=50,
        choices=OrderStatus.choices,
        default=OrderStatus.created,
        db_index=True
    )

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.SET_NULL,
        verbose_name='ресторан',
        related_name='restaurants',
        blank=True,
        null=True
    )

    comment = models.TextField(
        'комментарий',
        blank=True
    )

    registered_at = models.DateTimeField(
        'Дата создания',
        blank=True,
        db_index=True,
        default=timezone.now
    )
    called_at = models.DateTimeField(
        'Дата звонка',
        blank=True,
        null=True,
        db_index=True,
    )
    delivered_at = models.DateTimeField(
        'Дата доставки',
        blank=True,
        null=True,
        db_index=True,
    )

    payment_method = models.CharField(
        'Метод оплаты',
        max_length=50,
        choices=PaymentMethods.choices,
        default=PaymentMethods.card,
        db_index=True
    )

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f'{self.lastname} {self.firstname}, {self.address}'


class OrderProduct(models.Model):
    product = models.ForeignKey(
        Product,
        related_name='orders',
        verbose_name='товар',
        on_delete=models.CASCADE
    )

    order = models.ForeignKey(
        Order,
        related_name='products',
        verbose_name='заказ',
        on_delete=models.CASCADE
    )

    quantity = models.PositiveSmallIntegerField(
        verbose_name='количество',
        validators=[MinValueValidator(1)]
    )

    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name = 'элемент заказа'
        verbose_name_plural = 'элементы заказов'

    def __str__(self):
        return f'{self.order}, {self.product}, {self.quantity}'
