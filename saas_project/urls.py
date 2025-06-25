from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from core.forms import CustomAuthenticationForm
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),  # Inclure les URLs de l'app core
    path('login/', auth_views.LoginView.as_view(
        template_name='core/login.html',
        authentication_form=CustomAuthenticationForm
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(
        template_name='core/login.html',
        next_page='login'
    ), name='logout'),
    # Redirection de la racine vers l'inscription
    path('', RedirectView.as_view(url='register/', permanent=False)),
]
