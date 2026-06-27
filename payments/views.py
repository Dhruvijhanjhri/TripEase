from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
import uuid

from bookings.models import Booking
from .models import Payment
from .forms import PaymentForm
from packages.models import PackageBooking


@login_required
def payment_view(request, booking_id):

    booking = get_object_or_404(
        Booking,
        id=booking_id,
        user=request.user
    )

    if hasattr(booking, 'payment'):
        messages.info(
            request,
            'Payment already processed.'
        )

        return redirect(
            'bookings:detail',
            booking_reference=booking.booking_reference
        )

    if request.method == 'POST':

        form = PaymentForm(request.POST)

        if form.is_valid():

            payment_method = form.cleaned_data[
                'payment_method'
            ]

            try:

                with transaction.atomic():

                    transaction_id = uuid.uuid4().hex[:12].upper()

                    payment = Payment.objects.create(
                        booking=booking,
                        amount=booking.total_price,
                        payment_method=payment_method,
                        payment_status='success',
                        transaction_id=transaction_id
                    )

                    booking.booking_status = 'confirmed'
                    booking.save()

                    messages.success(
                        request,
                        f'Payment successful! '
                        f'Transaction ID: '
                        f'{transaction_id}'
                    )

                    return redirect(
                        'payments:success',
                        booking_id=booking_id
                    )

            except Exception as e:

                messages.error(
                    request,
                    f'Payment error: {str(e)}'
                )

    else:
        form = PaymentForm()

    context = {
        'booking': booking,
        'form': form,
    }

    return render(
        request,
        'payments/payment.html',
        context
    )

@login_required
def payment_success(
    request,
    booking_id
):

    booking = get_object_or_404(
        Booking,
        id=booking_id,
        user=request.user
    )

    payment = get_object_or_404(
        Payment,
        booking=booking
    )

    context = {
        'booking': booking,
        'payment': payment,
    }

    return render(
        request,
        'payments/success.html',
        context
    )

@login_required
def package_payment_view(
    request,
    booking_id
):

    booking = get_object_or_404(
        PackageBooking,
        id=booking_id,
        user=request.user
    )

    if hasattr(booking, 'payment'):

        messages.info(
            request,
            'Payment already processed.'
        )

        return redirect(
            'packages:booking_success',
            booking_id=booking.id
        )

    if request.method == 'POST':

        form = PaymentForm(
            request.POST
        )

        if form.is_valid():

            payment_method = form.cleaned_data[
                'payment_method'
            ]

            transaction_id = (
                uuid.uuid4()
                .hex[:12]
                .upper()
            )

            Payment.objects.create(
                package_booking=booking,
                amount=booking.total_price,
                payment_method=payment_method,
                payment_status='success',
                transaction_id=transaction_id
            )

            booking.booking_status = (
                'confirmed'
            )

            booking.save()

            return redirect(
                'payments:package_success',
                booking_id=booking.id
            )

    else:

        form = PaymentForm()

    return render(
        request,
        'payments/package_payment.html',
        {
            'booking': booking,
            'form': form
        }
    )

@login_required
def package_payment_success(
    request,
    booking_id
):

    booking = get_object_or_404(
        PackageBooking,
        id=booking_id,
        user=request.user
    )

    payment = get_object_or_404(
        Payment,
        package_booking=booking
    )

    return render(
        request,
        'payments/package_success.html',
        {
            'booking': booking,
            'payment': payment
        }
    )