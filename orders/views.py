from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Order

def create_order(request):
    if request.method == 'POST':
        # Example: order creation logic
        order = Order.objects.create(
            customer_name=request.POST.get('name'),
            email=request.POST.get('email'),
            address=request.POST.get('address'),
            total_price=request.POST.get('total_price')
        )
        order.save()
        messages.success(request, 'Your order has been placed successfully!')
        return redirect('order_success')
    return render(request, 'orders/create_order.html')

def order_success(request):
    return render(request, 'orders/order_success.html')

def order_history(request):
    orders = Order.objects.all().order_by('-id')
    return render(request, 'orders/order_history.html', {'orders': orders})
