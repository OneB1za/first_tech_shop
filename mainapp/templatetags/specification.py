from django import template
from django.utils.safestring import mark_safe
from mainapp.models import Smartphone
# РЕГИСТРИРУЕМ ТЕГ ?/
register = template.Library()

TABLE_HEAD = '''
<table class="table">
    <tbody>
    '''

TABLE_CONTENT = '''
    <tr>
        <td>{name}</td>
        <td>{value}</td>
    </tr>
'''

TABLE_TAIL = '''
    </tbody>
</table>
'''

PRODUCT_SPEC = {
    'notebook': {
        'Диагональ': 'diagonal',
        'Дисплей': 'display',
        'Частота процессора': 'processcor_freq',
        'Оперативка': 'ram',
        'Видюха': 'video',
        'Работа без дозарядки': 'time_without_charge',
    },

    'smartphone': {
        'Диагональ': 'diagonal',
        'Дисплей': 'display',
        'Разрешение': 'resolution',
        'Объем батареи': 'accum_volume',
        'Оперативка': 'ram',
        'Sd карта': 'sd',
        'Макс объем sd': 'sd_volume_max',
        'Разрешение главной камеры': 'main_cam_mp',
        'Разрешение фронтальной камеры': 'frontal_cam_mp'
    }
}


def get_product_spec(product, model_name):  # ПОЛУЧАЕМ ТИП ПРОДУКТА(НОУТ/МОБИЛКА) И ДОБАВЛЯЕМ В TABLE_CONTENT
    table_content = ''
    for name, value in PRODUCT_SPEC[model_name].items():
        table_content += TABLE_CONTENT.format(name=name, value=getattr(product, value))  # ДОБАВЛЯЕМ В TABLE_CONTENT
        # ЗНАЧЕНИЯ КОНКРЕТНОГО ПРОДУКТА
    return table_content


@register.filter  # ФИЛЬТР
def product_spec(product):

    model_name = product.__class__._meta.model_name  # УЗНАЕМ ИМЯ МОДЕЛИ
    if isinstance(product, Smartphone):
        if not product.sd:
            PRODUCT_SPEC['smartphone']['Макс объем sd'] = 'sd_volume_max'
        else:
            PRODUCT_SPEC['smartphone']['Макс объем sd'] = 'sd_volume_max'
    return mark_safe(TABLE_HEAD + get_product_spec(product, model_name) + TABLE_TAIL)  # КОНКАТЕНИРУЕМ ВСЕ
