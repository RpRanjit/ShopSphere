from django.core.mail import send_mail
from django.conf import settings

def send_order_confirmation_email(order):

    subject = f'ShopSphere - Order Confirmation #{order.id}'

    message = f"""
Hello {order.full_name},
Thank you for shooping with ShopSphere!
Your Order has been successfully placed.

Order Number: #{order.id}

Order Details:
"""
    for item in order.items.all():
        message += (
            f"\n{item.product_name}"
            f"\nQuantity: {item.quantity}"
            f"\nPrice: Rs. {item.price}"
            f"\nSubtotal: Rs. {item.subtotal}\n"
        )
    message += f"""
Total Amount: Rs {order.total_amount}

Shipping Address:
{order.shipping_address}

Thank you for choosing ShopSphere!
"""
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [order.email],
        fail_silently=False,
    )