from django.shortcuts import render
from django.views.generic import DetailView, View
from django.http import HttpResponseRedirect
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from .models import Notebook, Smartphone, Category, LatestProducts, CartProduct
from .mixins import CategoryDetailMixin, CartMixin


class BaseView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        categories = Category.objects.get_categories_for_side_bar()
        products = LatestProducts.objects.get_products_for_main_page('notebook', 'smart')
        context = {
            'categories': categories,
            'products': products,
            'cart': self.cart
        }
        return render(request, 'mainapp/base.html', context=context)


# Вьюха для шаблона product_detail.html, детально отображение
# чтобы не писать для каждой категории фьюху и шаблон, делаем такой хитровыебанный автоматизированную вьюху и шаблон потом
class ProductDetailView(CartMixin, CategoryDetailMixin, DetailView):
    CT_MODEL_MODEL_CLASS = {
        'notebook': Notebook,
        'smartphone': Smartphone
    }

    def dispatch(self, request, *args, **kwargs):
        # получаем конктреную модель которую будем отображать
        self.model = self.CT_MODEL_MODEL_CLASS[
            kwargs.get('ct_model')]  # распаковываем из dispatch kwargs и ищем там сt_model
        # ct_model в models.py и это | ct_model = obj.__class__._meta.model_name тоесть имя модели

        self.queryset = self.model._base_manager.all()  # получаем кверисет из бд
        return super().dispatch(request, *args, **kwargs)

    template_name = 'mainapp/product_detail.html'
    context_object_name = 'product'  # контекст для шаблона
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ct_model'] = self.model._meta.model_name
        return context


class CategoryDetailView(CartMixin, CategoryDetailMixin, DetailView):
    template_name = 'mainapp/category_detail.html'
    model = Category
    queryset = Category.objects.all()
    context_object_name = 'category'
    slug_url_kwarg = 'slug'


# products/noutbuki/macbook-pro-13/


class CartView(CartMixin,View):

    def get(self, request, *args, **kwargs):
        categories = Category.objects.get_categories_for_side_bar()
        context = {
            'cart': self.cart,
            'categories': categories
        }

        return render(request, 'mainapp/cart.html', context=context)


class AddToCartView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product, created = CartProduct.objects.get_or_create(
            user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=product.id, )

        if created:
            self.cart.products.add(cart_product)
        self.cart.save()
        messages.add_message(request, messages.INFO, 'Товар успешно добавлен')
        return HttpResponseRedirect('/cart/')


class DeleteFromCartView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product = CartProduct.objects.get(
            user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=product.id,
        )
        self.cart.products.remove(cart_product)
        cart_product.delete()
        self.cart.save()
        messages.add_message(request, messages.INFO, 'Товар успешно удален из корзины')
        return HttpResponseRedirect('/cart/')

class ChangeQtyView(CartMixin, View):

    def post(self, request, *args, **kwargs):
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product = CartProduct.objects.get(
            user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=product.id,
        )
        qty = int(request.POST.get('qty'))
        cart_product.qty = qty
        cart_product.save()
        self.cart.save()
        messages.add_message(request, messages.INFO, 'Кол-во товара успешно изменено')
        return HttpResponseRedirect('/cart/')

