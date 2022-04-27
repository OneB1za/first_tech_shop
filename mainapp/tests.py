from django.test import TestCase, RequestFactory
from decimal import Decimal
from .models import *
from .views import AddToCartView

User = get_user_model()


class ShopTestCases(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create(username='test_user', password='password')
        self.category = Category.objects.create(name='Ноутбуки', slug='notebooks')

        from django.core.files.uploadedfile import SimpleUploadedFile

        # костыль через байты по другому не получилось никак залить картинку ебанную
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile('small.gif', small_gif, content_type='image/gif')

        self.notebook = Notebook.objects.create(
            category=self.category,
            title='test_notebook',
            slug='test_slug',
            image=uploaded,
            price=Decimal('50000.00'),
            diagonal='73.3',
            display='ips',
            description='test_descrip',
            processcor_freq='3.4',
            ram='64',
            video='geforce gtx 1070',
            time_without_charge='10 hours',
        )
        self.customer = Customer.objects.create(user=self.user,
                                                phone='123456',
                                                address='address')
        self.cart = Cart.objects.create(owner=self.customer, final_price=self.notebook.price)
        self.cart_product = CartProduct.objects.create(
            cart=self.cart,
            user=self.customer,
            content_object=self.notebook

        )

    def test_add_2_cart(self):
        self.cart.products.add(self.cart_product)
        self.assertIn(self.cart_product, self.cart.products.all())
        self.assertEqual(self.cart.products.count(), 1)
        self.assertEqual(self.cart.final_price, Decimal('50000.00'))
    '''не законченный блок тестов'''
    def test_responce_from_add_2_cart_view(self):
        factory = RequestFactory()
        request = factory.get('')
        request.user = self.user
        #response = AddToCartView.as_view()(request, ct_model='notebooks', slug='test_slug')
        #self.assertEqual(response.status_code, 302)
