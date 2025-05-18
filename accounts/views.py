from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import SignUpForm


class RegisterView(CreateView):
    form_class = SignUpForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("accounts:login")        # after sign-up, go to login page


class UserLoginView(LoginView):
    template_name = "accounts/login.html"


class UserLogoutView(LogoutView):
    pass  # uses LOGOUT_REDIRECT_URL in settings
