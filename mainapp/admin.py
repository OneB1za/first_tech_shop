from django.contrib import admin
from django.forms import ModelChoiceField, ModelForm
from django.utils.safestring import mark_safe
from .models import *


admin.site.site_header = 'Административная панель управления'
admin.site.index_title = 'Контент'


class SmartphoneAdminForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if not instance.sd:
            self.fields['sd_volume_max'].widget.attrs.update({
                'readonly': True, 'style': 'background: lightgray'
            })

    def clean(self):
        if not self.cleaned_data['sd']:
            self.cleaned_data['sd_volume_max'] = None
        return self.cleaned_data


class NoteBookAdminForm(ModelForm):
    # ПРЕДУПРЕЖДАЮЩАЯ НАДПИСЬ
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # МЕСТО ГДЕ БУДЕТ И ТЕКСТ
        self.fields['image'].help_text = mark_safe(
            '<span style ="color:red; font-size:15px;">При загрузке изображения с разрешением больше - {}x{}, оно будет обрезано'.format(
                *Product.MAX_RESOLUTION
            )
        )


class PriceFilter(admin.SimpleListFilter):
    title = 'Цены'
    parameter_name = 'price'

    PRICE_LT_10K = 'Меньше 10к'
    PRICE_LT_25K = 'От 10к до 24к'
    PRICE_LT_50K = 'От 25к до 49к'
    PRICE_LT_75K = 'От 50к до 74к'
    PRICE_LT_100K = 'От 75к до 99к'
    PRICE_LT_150K = 'От 100к до 149к'
    PRICE_LT_200K = 'От 150к до 199к'
    PRICE_LT_250K = 'От 200к до 249к'
    REST = 'Остальное'

    def lookups(self, request, model_admin):
        return [
            (self.PRICE_LT_10K, 'до 10к руб'),
            (self.PRICE_LT_25K, 'от 10к до 24к'),
            (self.PRICE_LT_50K, 'От 25к до 49к'),
            (self.PRICE_LT_75K, 'От 50к до 74к'),
            (self.PRICE_LT_100K, 'От 75к до 99к'),
            (self.PRICE_LT_150K, 'От 100к до 149к'),
            (self.PRICE_LT_200K, 'От 150к до 199к'),
            (self.PRICE_LT_250K, 'От 200к до 249к'),
            (self.REST, 'Остальное'),
        ]

    def queryset(self, request, queryset):
        if self.value() == self.PRICE_LT_10K:
            return queryset.filter(price__lt=10000)
        elif self.value() == self.PRICE_LT_25K:
            return queryset.filter(price__lt=25000, price__gte=10000)
        elif self.value() == self.PRICE_LT_50K:
            return queryset.filter(price__lt=50000, price__gte=25000)
        elif self.value() == self.PRICE_LT_75K:
            return queryset.filter(price__lt=75000, price__gte=50000)
        elif self.value() == self.PRICE_LT_100K:
            return queryset.filter(price__lt=100000, price__gte=75000)
        elif self.value() == self.PRICE_LT_150K:
            return queryset.filter(price__lt=150000, price__gte=100000)
        elif self.value() == self.PRICE_LT_200K:
            return queryset.filter(price__lt=200000, price__gte=150000)
        elif self.value() == self.PRICE_LT_250K:
            return queryset.filter(price__lt=250000, price__gte=200000)
        elif self.value() == self.REST:
            return queryset.filter(price__gte=100000)


@admin.register(Smartphone)
class SmartphoneAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}  # авто заполнение слага через поле имени
    list_display = ['title', 'price', 'ram', 'main_cam_mp']
    search_fields = ['title']
    list_filter = [PriceFilter]
    list_per_page = 15
    form = SmartphoneAdminForm  # форма с предупреждающей надпись могу быть и любые другие
    change_form_template = 'mainapp/admin.html'  # жс для админки

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # условие проверки
        if db_field.name == 'category':
            # показывает не все категории а фильтрует и оставляет только ту в которую мы создаем
            # // тоесть - в при создании ноутбука ты можешь выбрать смартфон( в админке(пока))
            return ModelChoiceField(Category.objects.filter(slug='smartfony'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Notebook)
class NoteBookAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    list_display = ['title', 'price', 'ram', 'video']
    search_fields = ['title']
    list_filter = [PriceFilter]
    list_per_page = 15
    form = NoteBookAdminForm

    # тоже только для ноутов
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return ModelChoiceField(Category.objects.filter(slug='noutbuki'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ['name']
    search_fields = ['name']
    list_filter = ['name']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    fields = ('customer', 'first_name', 'last_name',
              'phone', 'address', 'delivery_type',
              'status', 'comment', 'order_date')
    list_display = ['customer', 'phone', 'address', 'status']
    list_filter = ['status', 'delivery_type']
    list_per_page = 15
    search_fields = ['customer', 'phone', 'address',
                     'first_name', 'last_name', 'comment']
    ordering = ['customer']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_per_page = 15
    list_display = ['id', 'owner', 'final_price', 'in_order', 'for_anonymous_user']
    search_fields = ['id']
    list_filter = ['in_order', 'for_anonymous_user']


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_per_page = 15
    list_display = ['user', 'phone', 'address']
    search_fields = ['user', 'phone']


@admin.register(CartProduct)
class CartProductAdmin(admin.ModelAdmin):
    list_per_page = 15
    list_display = ['user', 'cart', 'content_object', 'qty', 'final_price']
    search_fields = ['user', 'cart']

