from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from bookings.models import Booking
from .models import Payment
from .forms import PaymentForm
import random
import string


@login_required
def payment_view(request, booking_id):
    """Payment view"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    # Check if payment already exists
    if hasattr(booking, 'payment'):
        messages.info(request, 'Payment already processed for this booking.')
        return redirect('bookings:detail', booking_id=booking_id)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        
        if form.is_valid():
            payment_method = form.cleaned_data['payment_method']
            
            # Simulate payment processing
            # In real application, integrate with payment gateway
            try:
                with transaction.atomic():
                    # Generate transaction ID
                    transaction_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
                    
                    # Simulate payment success (90% success rate for demo)
                    payment_success = random.random() > 0.1
                    
                    payment = Payment.objects.create(
                        booking=booking,
                        amount=booking.total_price,
                        payment_method=payment_method,
                        payment_status='success' if payment_success else 'failed',
                        transaction_id=transaction_id if payment_success else None
                    )
                    
                    if payment_success:
                        booking.booking_status = 'confirmed'
                        booking.save()
                        messages.success(request, f'Payment successful! Transaction ID: {transaction_id}')
                        return redirect('payments:success', booking_id=booking_id)
                    else:
                        messages.error(request, 'Payment failed. Please try again.')
                        
            except Exception as e:
                messages.error(request, f'Payment error: {str(e)}')
    else:
        form = PaymentForm()
    
    context = {
        'booking': booking,
        'form': form,
    }
    
    return render(request, 'payments/payment.html', context)


@login_required
def payment_success(request, booking_id):
    """Payment success view"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    payment = get_object_or_404(Payment, booking=booking)
    
    context = {
        'booking': booking,
        'payment': payment,
    }
    
    return render(request, 'payments/success.html', context)






