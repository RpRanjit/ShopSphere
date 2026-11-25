from django.shortcuts import render, get_object_or_404, redirect
from products.models import Product
from django.views.decorators.http import require_POST

from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from .models import Cart, CartItem

# Create your views here.

def add_to_cart(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True 
    )

    if product.stock <= 0:
        return redirect('product_list')

    if request.user.is_authenticated:

        customer_cart, created = Cart.objects.get_or_create(
        user=request.user
        )

        cart_item, created = CartItem.objects.get_or_create(
        cart=customer_cart,
        product=product,
        defaults={'quantity': 1}
        )

        if not created:
            cart_item.quantity = min(
                cart_item.quantity + 1,
                product.stock
            )

            cart_item.save()

    else:

        cart = request.session.get('cart', {})

        product_id = str(product.id)

        current_quantity = cart.get(product_id, 0)

        cart[product_id] = min(
            current_quantity + 1,
            product.stock
        )

        request.session['cart'] = cart

    return redirect('product_list')


def cart_detail(request):

    cart_items = []
    total = 0

    if request.user.is_authenticated:

        customer_cart, created = Cart.objects.get_or_create(
            user=request.user
        )

        items = customer_cart.items.select_related('product')

        for item in items:

            product = item.product
            quantity = item.quantity

            if not product.is_active or product.stock <= 0:
                continue

            quantity = min(quantity, product.stock)

            subtotal = product.price * quantity

            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal,
            })

            total += subtotal

    else:

        cart = request.session.get('cart', {})

        for product_id, quantity in cart.items():

            product = get_object_or_404(
                Product,
                id=product_id,
                is_active=True
            )

            subtotal = product.price * quantity

            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal,
            })

            total += subtotal

    context = {
        'cart_items': cart_items,
        'total': total,
    }

    return render(request, 'cart/cart_detail.html', context)


@require_POST
def update_cart(request, product_id):

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        return redirect('cart_detail')

    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True
    )

    if product.stock <= 0:
        quantity = 0
    else:
        quantity = max(1, min(quantity, product.stock))

    if request.user.is_authenticated:

        customer_cart, created = Cart.objects.get_or_create(
            user=request.user
        )

        if quantity == 0:
            CartItem.objects.filter(
                cart=customer_cart,
                product=product
            ).delete()

        else:
            CartItem.objects.update_or_create(
                cart=customer_cart,
                product=product,
                defaults={'quantity': quantity}
            )

    else:

        cart = request.session.get('cart', {})
        product_id = str(product.id)

        if quantity == 0:
            cart.pop(product_id, None)
        else:
            cart[product_id] = quantity

        request.session['cart'] = cart

    return redirect('cart_detail')

@require_POST
def remove_from_cart(request, product_id):

    if request.user.is_authenticated:

        try:
            customer_cart = request.user.cart

            CartItem.objects.filter(
                cart=customer_cart,
                product_id=product_id
            ).delete()
        except Cart.DoesNotExist:
            pass
    else:

        cart = request.session.get('cart', {})

        product_id=str(product_id)

        cart.pop(product_id, None)

        request.session['cart'] = cart
    return redirect('cart_detail')




def customer_login(request):
    if request.method == "POST":
        form = AuthenticationForm(
            request,
            data=request.POST
        )

        if form.is_valid():
            user = form.get_user()

            auth_login(request, user)

            customer_cart, created = Cart.objects.get_or_create(user=user)

            existing_items = customer_cart.items.select_related('product')

            session_cart = request.session.get('cart', {})

            # Load products already saved in the customer's cart

            merged_cart = {}

            for item in customer_cart.items.select_related('product'):

                product = item.product

                if product.is_active and product.stock > 0:

                    merged_cart[str(product.id)] = min(
                        item.quantity,
                        product.stock
                    )
            # Merge products from the guest session cart
            for product_id, quantity in session_cart.items():

                product = Product.objects.filter(
                    id=product_id,
                    is_active=True
                ).first()

                if product is None or product.stock <= 0:
                    continue

                try:
                    quantity = int(quantity)
                except (TypeError, ValueError):
                    continue

                if quantity <= 0:
                    continue

                product_id = str(product.id)

                existing_quantity = merged_cart.get(product_id, 0)

                merged_cart[product_id] = min(
                    existing_quantity + quantity,
                    product.stock
                )
            # save the merged cart in the database
            for product_id, quantity in merged_cart.items():

                product = Product.objects.get(id=product_id)

                CartItem.objects.update_or_create(
                    cart=customer_cart,
                    product=product,
                    defaults={
                        'quantity': quantity
                    }
                )

            # keep the session cart synchronized

            request.session['cart'] = merged_cart

            return redirect('product_list')
    else:
        form = AuthenticationForm()

    context = {
        'form': form,
        'next': request.GET.get('next', '')
    }

    return render(
        request, 'registration/login.html', context
    )
