from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
# Create your tests here.

from .models import Order
from products.models import Product
from cart.models import Cart, CartItem
from orders.models import Order, OrderItem


class OrderHistoryTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testcustomer',
            password='TestPass123!'
        )

        self.order = Order.objects.create(
            user=self.user,
            full_name='Test Customer',
            email='test@example.com',
            phone='9800000000',
            shipping_address='Test Address',
            total_amount='5000.00',
        )
    def test_logged_in_customer_can_view_order_history(self):
        self.client.login(
            username='testcustomer',
            password='TestPass123!',
        )

        response = self.client.get('/orders/my-orders/')

        self.assertEqual(response.status_code, 200)
        # self.assertContains(response, 'Test Customer')
        self.assertContains(response, '5000.00')

    def test_customer_only_sees_their_own_orders(self):
        another_user = User.objects.create_user(
            username='anothercustomer',
            password='TestPass123!'
        )

        Order.objects.create(
            user=another_user,
            full_name='Another Customer',
            email='another@example.com',
            phone='9811111111',
            shipping_address='Another Address',
            total_amount='9000.00',
        )

        self.client.login(
            username='testcustomer',
            password='TestPass123!'
        )

        response = self.client.get('/orders/my-orders/')

        # self.assertContains(response, 'Test Customer')
        self.assertContains(response, '5000.00')
        self.assertNotContains(response, '9000.00')


class CheckoutAccessTest(TestCase):

    def test_guest_cannot_open_checkout(self):
        response = self.client.get(reverse('checkout'))

        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)


class CheckOutTest(TestCase):
    def test_decimal_creates_order_and_updates_stock(self):
        user = User.objects.create_user(
            username='checkoutcustomer',
            password='testpassword123'
        )

        product = Product.objects.create(
            name='Test Laptop',
            description='Laptop fro checkout testing',
            price=Decimal('5000.00'),
            stock=5,
            is_active=True
        )

        cart=Cart.objects.create(user=user)

        CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=2
        )

        self.client.login(
            username='checkoutcustomer',
            password="testpassword123"
        )

        response = self.client.post(
            reverse('checkout'),
            {
             'full_name': 'Test Customer',
             'email': 'test@example.com',
             'phone': '9800000000',
             'shipping_address': 'Test Address, Nepal',   
            }
        )

        self.assertEqual(response.status_code, 302)

        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 1)

        order = Order.objects.get(user=user)
        order_item = OrderItem.objects.get(order=order)

        self.assertEqual(order.total_amount, Decimal('10000.00'))
        self.assertEqual(order_item.quantity, 2)

        product.refresh_from_db()
        self.assertEqual(product.stock, 3)

        self.assertEqual(cart.items.count(), 0)



    def test_checkout_rejects_quantity_above_stock(self):
        user = User.objects.create_user(
            username='stockcustomer',
            password='testpassword123'
        )

        product = Product.objects.create(
            name='Limited Stock Laptop',
            description='laptop with limite stock',
            price=Decimal('5000.00'),
            stock=3,
            is_active=True
        )

        cart = Cart.objects.create(user=user)

        CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=5
        )

        # login_success = self.client.login(
        #     username='stockcustomer',
        #     passsword='testpassword123'
        # )

        # print('Login Successfull:', login_success)
        # self.assertTrue(login_success)
        self.client.force_login(user)


        response = self.client.post(
            reverse('checkout'),
            {
                'full name': 'Stock Customer',
                'email': 'stock@example.com',
                'phone': '9800000000',
                'shipping_address': 'Test Address, Nepal'
            }
        )
        # print("Checkout redirected to:", response.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(OrderItem.objects.count(), 0)

        product.refresh_from_db()
        self.assertEqual(product.stock, 3)

        self.assertEqual(cart.items.count(), 1)


    def test_checkout_rejects_empty_cart(self):

        user = User.objects.create_user(
            username='emptycartcustomer',
            password='testpassword123'
        )

        Cart.objects.create(user=user)

        self.client.force_login(user)

        response = self.client.post(
            reverse('checkout'),
                {
                    'full_name': 'Empty Cart Customer',
                    'email': 'empty@example.com',
                    'phone': '9800000000',
                    'shipping_address': 'Test Address, Nepal',
                }
                    )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(OrderItem.objects.count(), 0)

    def test_checkout_rejects_inactive_product(self):
        user = User.objects.create_user(
            username='inactivecustomer',
            password='testpassword123'
        )

        product = Product.objects.create(
            name='Inactive Laptop',
            description='This product is unavailable',
            price=Decimal('5000.00'),
            stock=5,
            is_active=False
        )

        cart = Cart.objects.create(user=user)

        CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=1
        )

        self.client.force_login(user)

        response = self.client.post(
            reverse('checkout'),
            {
                'full_name': 'Inactive Customer',
                'email': 'inactive@example.com',
                'phone': '9800000000',
                'shipping_address': 'Test Address, Nepal',
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(OrderItem.objects.count(), 0)

        product.refresh_from_db()
        self.assertEqual(product.stock, 5)

        self.assertEqual(cart.items.count(), 1)