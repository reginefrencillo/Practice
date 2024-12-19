from django.core.mail import send_mail
from django.shortcuts import render, redirect
from .forms import UserRegistrationForm
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model

User = get_user_model()  # Custom or default user model

def register(request):
    """
    Handles user registration and sends an email for account activation.
    """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Save the user but deactivate the account until email confirmation
            user = form.save(commit=False)
            user.is_active = False  
            user.save()

            # Prepare email data
            current_site = get_current_site(request)
            subject = 'Activate Your Account'
            message = render_to_string('user/activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })

            # Send activation email
            send_mail(
                subject,
                message,
                'admin@example.com',  # Replace with your email address
                [user.email],
                fail_silently=False,  # Set to True in production to suppress email errors
            )

            # Redirect to a registration complete page
            return render(request, 'user/registration_complete.html')
    else:
        # Render the registration form for GET requests
        form = UserRegistrationForm()

    # Render the registration page
    return render(request, 'user/register.html', {'form': form})


from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('user:login')
    else:
        return render(request, 'user/activation_invalid.html')

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages

def user_login(request):
    """
    Handles user login.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            # Redirect to the appropriate dashboard based on user role
            return redirect('login_success')  # Redirect to the login success view
        else:
            messages.error(request, 'Invalid username or password')
            return redirect('login')  # Or render the login page again
        
    return render(request, 'user/login.html')  # Render login page on GET request


