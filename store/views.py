from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Location, Category
from django.core.mail import send_mail
from django.conf import settings
from decimal import Decimal, InvalidOperation

from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib import messages

from orders.models import Order, OrderItem


# ------------------ Checkout ------------------ #
def checkout(request):
    cart = Cart(request)

    if len(cart) == 0:
        return redirect('cart_detail')  # Redirect if cart is empty

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        if not (name and email and phone and address):
            error = "All fields are required!"
            return render(request, 'store/checkout.html', {'cart': cart, 'error': error})

        # Build email content with all cart items
        items_text = ""
        for item in cart:
            items_text += f"{item['product'].name} - {item['quantity']} x ₹{item['price']} = ₹{item['total_price']}\n"

        email_message = f"""
Order Confirmation

Hello {name},

Thank you for your order!

Phone: {phone}
Delivery Address: {address}

Order Details:
{items_text}

Total Amount: ₹{cart.get_total_price()}
"""

        # Send email
        send_mail(
            'Order Confirmation',
            email_message,
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

        # Clear cart after order
        request.session['cart'] = {}
        request.session.modified = True

        return render(request, 'store/checkout_success.html', {'name': name, 'cart': cart})

    return render(request, 'store/checkout.html', {'cart': cart})


# ------------------ Home & Product ------------------ #
def home(request):
    selected_location = request.GET.get('location')
    selected_category = request.GET.get('category')

    # If user selects a location, save it in session
    if selected_location:
        request.session['selected_location'] = selected_location
    else:
        # If not selected, try to get from session
        selected_location = request.session.get('selected_location')

    locations = Location.objects.all()
    categories = Category.objects.all()
    products = Product.objects.all()

    if selected_location:
        products = products.filter(location__id=selected_location)
        try:
            selected_location_obj = Location.objects.get(id=selected_location)
            selected_location_name = selected_location_obj.name
        except Location.DoesNotExist:
            selected_location_name = None
    else:
        selected_location_name = None

    if selected_category:
        products = products.filter(category__id=selected_category)

    context = {
        'products': products,
        'locations': locations,
        'categories': categories,
        'selected_location': selected_location,
        'selected_location_name': selected_location_name,
        'selected_category': selected_category,
    }
    return render(request, 'store/home.html', context)


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    related_products = Product.objects.exclude(id=product.id)[:4]
    return render(request, 'store/product_detail.html', {
        'product': product,
        'related_products': related_products
    })


# ------------------ Cart Class ------------------ #
class Cart:
    """Session-based shopping cart (Decimal-based for price accuracy)"""
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.price)
            }

        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            quantity = 1

        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity

        self.save()

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def save(self):
        self.session['cart'] = self.cart
        self.session.modified = True

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)

        for product in products:
            item = self.cart[str(product.id)]

            try:
                price = Decimal(item['price'])
            except (InvalidOperation, TypeError, ValueError):
                price = Decimal('0.00')

            quantity = int(item['quantity'])
            item['product'] = product
            item['price'] = price
            item['total_price'] = price * quantity

            yield item

    def __len__(self):
        """Return total quantity of items in cart"""
        return sum(int(item['quantity']) for item in self.cart.values())

    def get_total_price(self):
        """Accurate total with Decimal"""
        total = Decimal('0.00')
        for item in self.cart.values():
            try:
                price = Decimal(item['price'])
                quantity = int(item['quantity'])
            except (InvalidOperation, ValueError, TypeError):
                continue
            total += price * quantity
        return total


# ------------------ Cart Views ------------------ #
def add_to_cart(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.add(product=product, quantity=1)
    return redirect('cart_detail')


def remove_from_cart(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart_detail')


def update_cart(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    try:
        quantity = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        quantity = 1
    cart.add(product=product, quantity=quantity, override_quantity=True)
    return redirect('cart_detail')


def cart_detail(request):
    cart = Cart(request)

    # Get selected location from session
    selected_location = request.session.get('selected_location')
    selected_location_name = None

    if selected_location:
        try:
            selected_location_obj = Location.objects.get(id=selected_location)
            selected_location_name = selected_location_obj.name
        except Location.DoesNotExist:
            pass

    return render(request, 'store/cart.html', {
        'cart': cart,
        'selected_location': selected_location,
        'selected_location_name': selected_location_name,
        'locations': Location.objects.all(),  # needed for popup
    })


# produt page all showing
def properties_by_location(request, location_id=None):
    locations = Location.objects.all()
    selected_location = None
    products = Product.objects.all()

    if location_id:
        selected_location = get_object_or_404(Location, id=location_id)
        products = products.filter(location=selected_location)

    context = {
        'locations': locations,
        'selected_location': selected_location,
        'products': products
    }
    return render(request, 'store/properties.html', context)

# subscription
def subscribe(request):
    if request.method == "POST":
        email = request.POST.get('email')
        
        # Send confirmation mail to user
        subject = "Subscription Successful!"
        message = f"Hi {email},\n\nThank you for subscribing to our newsletter! We'll keep you updated."
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]

        try:
            send_mail(subject, message, from_email, recipient_list)
            messages.success(request, "Subscription successful! Check your inbox for confirmation.")
        except Exception as e:
            messages.error(request, f"Error sending email: {e}")

        return redirect('home')  # redirect to your homepage or thank-you page
    

    # order
def place_order(request):
    cart = request.session.get('cart', {})
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        address = request.POST['address']

        total_price = sum(item['price'] * item['quantity'] for item in cart.values())
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            name=name,
            email=email,
            phone=phone,
            address=address,
            total_price=total_price
        )

        for item_id, item in cart.items():
            product = Product.objects.get(id=item_id)
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item['quantity'],
                price=item['price']
            )

        request.session['cart'] = {}  # Clear cart after order
        return render(request, 'thankyou.html', {'name': name, 'cart': cart, 'total_price': total_price})  

    # detailpage

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))

    # Create a session-based cart if not exist
    cart = request.session.get('cart', {})

    if str(product_id) in cart:
        cart[str(product_id)]['quantity'] += quantity
    else:
        cart[str(product_id)] = {
            'name': product.name,
            'price': float(product.price),
            'quantity': quantity,
            'image': product.image.url,
        }

    request.session['cart'] = cart
    messages.success(request, f'{product.name} ({quantity}) added to your cart!')
    return redirect('product_detail', product_id=product_id)  