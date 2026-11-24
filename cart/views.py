from django.shortcuts import render, get_object_or_404, redirect
from products.models import Product
from django.views.decorators.http import require_POST

# Create your views here.

def add_to_cart(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True 
    )

    cart = request.session.get('cart', {})

    product_id = str(product.id)

    if product_id in cart:

        cart[product_id] += 1
    
    else:
        cart[product_id] = 1

    request.session['cart'] = cart

    return redirect('product_list')

def cart_detail(request):

    cart = request.session.get('cart', {})

    cart_items = []
    total = 0

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

    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True
    )

    quantity = int(request.POST.get('quantity', 1))

    if quantity < 1:
        quantity = 1
    if quantity > product.stock:
        quantity = product.stock

    cart = request.session.get('cart',{})

    product_id=str(product.id)

    if quantity == 0:
        cart.pop(product_id, None)
    else:
        cart[product_id] = quantity

    request.session['cart'] = cart

    return redirect('cart_detail')


@require_POST
def remove_from_cart(request, product_id):

    cart = request.session.get('cart', {})

    product_id = str(product_id)

    cart.pop(product_id, None)

    request.session['cart'] = cart

    return redirect('cart_detail')