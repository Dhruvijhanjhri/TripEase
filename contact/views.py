from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactForm


def contact_view(request):
    """Contact form view"""
    if request.method == 'POST':
        form = ContactForm(request.POST, request.FILES)
        
        if form.is_valid():
            contact_message = form.save(commit=False)
            if request.user.is_authenticated:
                contact_message.user = request.user
            contact_message.save()
            
            messages.success(request, 'Thank you for contacting us! We will get back to you soon.')
            return redirect('contact:contact')
    else:
        form = ContactForm()
        if request.user.is_authenticated:
            form.fields['name'].initial = request.user.get_full_name()
            form.fields['email'].initial = request.user.email
            form.fields['phone'].initial = request.user.phone
    
    return render(request, 'contact/contact.html', {'form': form})

