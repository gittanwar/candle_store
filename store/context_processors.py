# store/context_processors.py
from decimal import Decimal, InvalidOperation
from .models import Location

def global_context(request):
    locations = Location.objects.all()

    # Selected location
    selected_location_id = request.session.get('selected_location')
    selected_location_name = None
    if selected_location_id:
        try:
            selected_location_name = Location.objects.get(id=selected_location_id).name
        except Location.DoesNotExist:
            selected_location_name = None

    # Cart: read exactly how Cart() stores it and compute consistent values
    cart_session = request.session.get('cart', {}) or {}
    cart_items_count = 0       # total quantity (sum of quantities)
    cart_unique_count = 0      # number of unique products
    cart_total_amount = Decimal('0.00')

    if isinstance(cart_session, dict):
        cart_unique_count = len(cart_session)
        for pid, data in cart_session.items():
            # Defensive casts: accept quantity as str/int, price as str/Decimal
            try:
                quantity = int(data.get('quantity', 0))
            except (TypeError, ValueError):
                quantity = 0

            price_val = data.get('price', '0')
            try:
                price = Decimal(str(price_val))
            except (InvalidOperation, TypeError, ValueError):
                price = Decimal('0.00')

            cart_items_count += quantity
            cart_total_amount += price * quantity

    return {
        'locations': locations,
        'selected_location': selected_location_id,
        'selected_location_name': selected_location_name,
        # Expose both types of counts and total price so you can choose in template:
        'cart_count': cart_items_count,          # sum of quantities (default)
        'cart_unique_count': cart_unique_count,  # number of unique products
        'cart_total_amount': cart_total_amount,  # Decimal
    }
