from django.contrib import admin
from django.forms import ModelChoiceField, ModelForm
from django.utils.safestring import mark_safe
from .models import *

admin.site.register(CartProduct)
admin.site.register(Cart)
admin.site.register(Customer)


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


@admin.register(Smartphone)
class SmartphoneAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}  # авто заполнение слага через поле имени
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
    form = NoteBookAdminForm

    # тоже только для ноутов
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return ModelChoiceField(Category.objects.filter(slug='noutbuki'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    ordering = []
