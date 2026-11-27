from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import CheckoutForm

from .email import send_order_confirmation_email

from decimal import Decimal
from cart.models import Cart

from django.shortcuts import redirect, get_object_or_404
from django.db import transaction

from products.models import Product
from .models import Order, OrderItem
# Create your views here.

@login_required
def checkout(request):
    customer_cart, created = Cart.objects.get_or_create(
        user=request.user
    )

    form = CheckoutForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():

        cart_items = list(
            customer_cart.items.select_related('product')
        )

        if not cart_items:
            form.add_error(None, 'Your cart is empty.')

        else:
            try:
                with transaction.atomic():

                    locked_products = {}
                    total_amount = Decimal('0.00')

                    # Validate stock and calculate the real total
                    for item in cart_items:
                        product = Product.objects.select_for_update().get(
                            pk=item.product_id
                        )

                        if not product.is_active:
                            raise ValueError(
                                f'{product.name} is no longer available.'
                            )

                        if product.stock < item.quantity:
                            raise ValueError(
                                f'Not enough stock for {product.name}. '
                                f'Available stock: {product.stock}.'
                            )

                        locked_products[product.id] = product

                        total_amount += (
                            product.price * item.quantity
                        )

                    # Create the order from the validated form
                    order = form.save(commit=False)
                    order.user = request.user
                    order.total_amount = total_amount
                    order.save()

                    # Create order items and reduce stock
                    for item in cart_items:
                        product = locked_products[item.product_id]

                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            product_name=product.name,
                            price=product.price,
                            quantity=item.quantity,
                        )

                        product.stock -= item.quantity
                        product.save(update_fields=['stock'])

                    # Clear the customer's database cart
                    customer_cart.items.all().delete()

                    transaction.on_commit(
                        lambda: send_order_confirmation_email(order),
                        robust=True
                    )

                return redirect(
                    'order_confirmation',
                    order_id=order.id
                )

            except ValueError as error:
                form.add_error(None, str(error))

    cart_items = customer_cart.items.select_related('product')

    checkout_items = []
    total_amount = Decimal('0.00')

    for item in cart_items:
        subtotal = item.product.price * item.quantity

        checkout_items.append({
            'product': item.product,
            'quantity': item.quantity,
            'subtotal': subtotal,
        })

        total_amount += subtotal

    return render(
        request,
        'orders/checkout.html',
        {
            'form': form,
            'checkout_items': checkout_items,
            'total_amount': total_amount,
        }
    )


@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related('items'),
        id=order_id,
        user=request.user,
    )

    return render(
        request,
        'orders/confirmation.html',
        {'order': order}
    )


@login_required
def order_history(request):
    orders = Order.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(
        request,
        'orders/order_history.html',
        {'orders': orders}
    )