from django.shortcuts import render,get_object_or_404, redirect
from .models import Product, Category
from django.db.models import Q
from django.contrib.auth.forms import UserCreationForm
# Create your views here.


def product_list(request):

    category_id = request.GET.get('category')

    search_query = request.GET.get('q')

    categories = Category.objects.all()

    products = Product.objects.filter(is_active=True)

    if category_id:
        products = products.filter(category_id=category_id)

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query)
        ) | products.filter(
            Q(description__icontains=search_query)
        )

    sort_by = request.GET.get('sort')

    sort_options = {
        'price_low': 'price',
        'price_high': '-price',
        'name': 'name',
        'newest': '-created_at'
    }

    if sort_by in sort_options:
        products = products.order_by(sort_options[sort_by])
    else:
        products = products.order_by('name')

    context = {
        'products': products,
        'categories': categories,
        'selected_category': category_id,
        'search_query': search_query,
        'sort_by': sort_by
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


def register(request):

    if request.method == "POST": 

        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()

    context = {
        'form': form
        }

    return render(request, 'registration/register.html', context)