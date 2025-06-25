from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Liste des URLs qui ne nécessitent pas d'authentification
        public_urls = [reverse('login'), reverse('register'), reverse('admin:index')]
        
        # Si l'utilisateur est authentifié et essaie d'accéder aux pages de login/register
        if request.user.is_authenticated:
            if request.path in [reverse('login'), reverse('register')]:
                if request.user.is_admin():
                    return redirect('dashboard_admin')
                return redirect('dashboard_user')
            
            # Redirection selon le rôle pour les dashboards
            if request.path == reverse('dashboard_admin') and not request.user.is_admin():
                messages.error(request, 'Accès non autorisé au dashboard administrateur.')
                return redirect('dashboard_user')
            elif request.path == reverse('dashboard_user') and request.user.is_admin():
                return redirect('dashboard_admin')
        
        # Si l'utilisateur n'est pas authentifié et essaie d'accéder à une page protégée
        elif not request.user.is_authenticated and request.path not in public_urls:
            messages.warning(request, 'Veuillez vous connecter pour accéder à cette page.')
            return redirect('login')

        response = self.get_response(request)
        return response