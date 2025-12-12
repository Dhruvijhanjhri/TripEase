from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'booking', 'amount', 'payment_method', 'payment_status', 'payment_date')
    list_filter = ('payment_status', 'payment_method', 'payment_date')
    search_fields = ('transaction_id', 'booking__booking_reference', 'booking__user__email')
    date_hierarchy = 'payment_date'
    ordering = ('-payment_date',)
    readonly_fields = ('payment_date', 'updated_at')



