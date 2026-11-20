from django.shortcuts import render,get_object_or_404
from .models import Product, Category
# Create your views here.

def product_list(request):

    category_id = request.GET.get('category')

    categories = Category.objects.all()

    products = Product.objects.filter(is_active=True)

    if category_id:
        products = products.filter(category_id=category_id)

    context = {
        'products': products,
        'categories': categories,
        'selected_category': category_id
    }

    return render(request, 'products/product_list.html', context)

def product_detail(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True
    )

    context = {
        'product': product
    }

    return render(request, 'products/product_detail.html', context)