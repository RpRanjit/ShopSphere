from cart.models import Cart

def cart_count(request):
    if request.user.is_authenticated:

        try:
            customer_cart = request.user.cart

            count = sum(
                item.quantity
                for item in customer_cart.items.all()
            )

        except Cart.DoesNotExist:
            count = 0
    else:

        cart = request.session.get('cart', {})

        count = sum(cart.values())

    return {
        'cart_count': count
    }