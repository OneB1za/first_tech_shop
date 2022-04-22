from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.urls import reverse

from PIL import Image

import sys

from io import BytesIO

User = get_user_model()


def get_models_for_count(*model_names):  # функция для подсчета товара в каждой из категорий
    # проходимся по всем именам категорий
    # и считаем для каждой каунт
    return [models.Count(model_name) for model_name in model_names]


def get_product_url(obj, viewname):
    ct_model = obj.__class__._meta.model_name  # имя конкретной модели для отображегия урла
    return reverse(viewname, kwargs={'ct_model': ct_model, 'slug': obj.slug})


class MinResolutionErrorException(Exception):
    pass


class MaxResolutionErrorException(Exception):
    pass


class CategoryManager(models.Manager):
    CATEGORY_NAME_COUNT_NAME = {
        'Ноутбуки': 'notebook__count',
        'Смартфоны': 'smartphone__count',
    }

    def get_queryset(self):
        return super().get_queryset()

    def get_categories_for_side_bar(self):
        # создаем переменную с моделями
        models = get_models_for_count('notebook', 'smartphone')
        qs = list(self.get_queryset().annotate(*models))

        data = [
            dict(name=c.name, url=c.get_absolute_url(), count=getattr(c, self.CATEGORY_NAME_COUNT_NAME[c.name]))
            for c in qs
        ]
        return data

        # return [dict(name=c['name'], slug=c['slug'], count=c[self.CATAGORY_NAME_COUNT_NAME[c['name']]]) for c in qs]


class LatestProductsManager:

    @staticmethod
    def get_products_for_main_page(*args, **kwargs):
        with_respect_to = kwargs.get('with_respect_to')
        products = []  # all Products
        ct_models = ContentType.objects.filter(model__in=args)  # ct - Content_type
        for ct_model in ct_models:
            product = ct_model.model_class()._base_manager.all().order_by('-id')[:5]  # Select the last 5
            products.extend(product)

        if with_respect_to:
            ct_model = ContentType.objects.filter(model=with_respect_to)
            if ct_model.exists():
                if with_respect_to in args:
                    return sorted(products, key=lambda x: x.__class__._meta.model_name
                                  .startswith(with_respect_to), reverse=True)
        return products


class LatestProducts:
    objects = LatestProductsManager()


class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name='Имя категории')
    slug = models.SlugField(unique=True)
    objects = CategoryManager()

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.name


class Product(models.Model):
    MIN_RESOLUTION = (450, 300)
    MAX_RESOLUTION = (451, 301)
    MAX_IMAGE_SIZE = 3145728

    class Meta:
        abstract = True

    category = models.ForeignKey(Category, verbose_name='Категория', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, verbose_name='Наименование')
    slug = models.SlugField(unique=True)
    image = models.ImageField(verbose_name='Изображение товара')
    description = models.TextField(verbose_name='Описание', null=True)
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Цена')

    def __str__(self):
        return f'{self.title}'

    def save(self, *args, **kwargs):
        image = self.image
        img = Image.open(image)
        new_img = img.convert('RGB')
        resized_new_img = new_img.resize((450, 300), Image.ANTIALIAS)
        filestream = BytesIO()
        resized_new_img.save(filestream, 'JPEG', quality=90)
        filestream.seek(0)
        img_name = '{}.{}'.format(*self.image.name.split('.'))
        self.image = InMemoryUploadedFile(
            filestream, 'ImageField', img_name, 'jpeg/image', sys.getsizeof(filestream), None
        )

        super().save(*args, **kwargs)


class Notebook(Product):
    diagonal = models.CharField(max_length=255, verbose_name='Диагональ')
    display = models.CharField(max_length=255, verbose_name='Тип дисплея')
    processcor_freq = models.CharField(max_length=255, verbose_name='Частота процессора')
    ram = models.CharField(max_length=255, verbose_name='Оперативка')
    video = models.CharField(max_length=255, verbose_name='Видюха')
    time_without_charge = models.CharField(max_length=255, verbose_name='Работа без дозарядки')

    def __str__(self):
        return f'{self.category.name}: {self.title}'

    def get_absolute_url(self):
        return get_product_url(self, 'product_detail')


class Smartphone(Product):
    SIXTEEN = '16'
    THIRTY_TWO = '32'
    SIXTY_FOUR = '64'
    ONE_HUNDRED_TWENTY_EIGHT = '128'
    TWO_HUNDRED_FIFTY_SIX = '256'

    CHOICE_SD_VOLUME_MAX = [
        (SIXTEEN, 16),
        (THIRTY_TWO, 32),
        (SIXTY_FOUR, 64),
        (ONE_HUNDRED_TWENTY_EIGHT, 128),
        (TWO_HUNDRED_FIFTY_SIX, 256),
    ]

    diagonal = models.CharField(max_length=255, verbose_name='Диагональ')
    display = models.CharField(max_length=255, verbose_name='Тип дисплея')
    resolution = models.CharField(max_length=255, verbose_name='Разрешение')
    accum_volume = models.CharField(max_length=255, verbose_name='Объем батареи')
    ram = models.CharField(max_length=255, verbose_name='Оперативка')
    sd = models.BooleanField(default=True, verbose_name='Sd карта')
    # sd_volume_max = models.CharField(max_length=255, null=True, blank=True, verbose_name='Максимальный объем встраиваемой памяти')
    sd_volume_max = models.CharField(choices=CHOICE_SD_VOLUME_MAX, max_length=40, null=True,
                                     blank=True, verbose_name='Максимальный объем встраиваемой памяти')
    main_cam_mp = models.CharField(max_length=255, verbose_name='Разрешение главной камеры')
    frontal_cam_mp = models.CharField(max_length=255, verbose_name='Разрешение фронтальной камеры')

    def __str__(self):
        return f'{self.category.name}: {self.title}'

    def get_absolute_url(self):
        return get_product_url(self, 'product_detail')


class CartProduct(models.Model):
    user = models.ForeignKey('Customer', verbose_name='Покупатель', on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', verbose_name='Корзина', on_delete=models.CASCADE, related_name='related_products')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    # product = models.ForeignKey(Product, verbose_name='Товар', on_delete=models.CASCADE)
    qty = models.PositiveIntegerField(default=1, verbose_name='Количество')
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Итоговая цена')

    def __str__(self):
        return f'Продукт: {self.content_object.title}(Для корзины)'

    def save(self, *args, **kwargs):
        self.final_price = self.qty * self.content_object.price
        super().save(*args, **kwargs)

class Cart(models.Model):
    owner = models.ForeignKey('Customer', verbose_name='Владелец', on_delete=models.CASCADE)
    products = models.ManyToManyField(CartProduct, blank=True, related_name='related_cart')
    total_products = models.PositiveIntegerField(default=0)
    final_price = models.DecimalField(max_digits=9, default=0, decimal_places=2, verbose_name='Итоговая цена')
    in_order = models.BooleanField(default=False)
    for_anonymous_user = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)


class Customer(models.Model):
    # емайл фирст и ласт нейм есть в базовом юзере которого создали выше
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, verbose_name='Номер телефона')
    address = models.CharField(max_length=255, verbose_name='Адрес')

    def __str__(self):
        return 'Покупатель {} {}'.format(self.user.first_name, self.user.last_name)
