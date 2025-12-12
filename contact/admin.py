from django.contrib import admin
from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'name', 'email', 'phone', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('subject', 'name', 'email', 'message')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('user', 'name', 'email', 'phone')
        }),
        ('Message', {
            'fields': ('subject', 'message', 'attachment')
        }),
        ('Status', {
            'fields': ('status', 'created_at', 'updated_at')
        }),
    )



