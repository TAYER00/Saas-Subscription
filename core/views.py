from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from django.utils import timezone
from .models import CustomUser, Subscription, Notification, SubscriptionPack
from .forms import CustomUserCreationForm

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Créer un abonnement inactif
            subscription = Subscription.objects.create(user=user)
            # Créer une notification de bienvenue
            Notification.objects.create(
                user=user,
                type='system',
                title='Bienvenue !',
                message='Bienvenue sur notre plateforme. Choisissez un pack pour commencer.'
            )
            messages.success(request, 'Inscription réussie ! Vous pouvez maintenant vous connecter.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'core/register.html', {'form': form})

@login_required
def dashboard_user(request):
    user = request.user
    subscription = user.subscription
    notifications = user.notifications.filter(is_read=False)[:5]
    return render(request, 'core/dashboard_user.html', {
        'subscription': subscription,
        'notifications': notifications
    })

@login_required
def dashboard_admin(request):
    if not request.user.is_admin():
        messages.error(request, 'Accès non autorisé.')
        return redirect('dashboard_user')
    
    total_users = CustomUser.objects.filter(role='user').count()
    active_subscriptions = Subscription.objects.filter(is_active=True).count()
    recent_users = CustomUser.objects.filter(role='user').order_by('-date_joined')[:10]
    subscription_notifications = Notification.objects.filter(
        type='subscription',
        is_read=False
    ).order_by('-created_at')

    return render(request, 'core/dashboard_admin.html', {
        'total_users': total_users,
        'active_subscriptions': active_subscriptions,
        'recent_users': recent_users,
        'subscription_notifications': subscription_notifications
    })

@login_required
def subscription_packs(request):
    if request.user.subscription.is_active:
        messages.warning(request, 'Vous avez déjà un abonnement actif.')
        return redirect('dashboard_user')
    return render(request, 'core/subscription_packs.html')

@login_required
def confirm_subscription(request, pack_type):
    if request.user.subscription.is_active:
        messages.warning(request, 'Vous avez déjà un abonnement actif.')
        return redirect('dashboard_user')

    try:
        pack = SubscriptionPack.objects.get(name=pack_type)
    except SubscriptionPack.DoesNotExist:
        messages.error(request, 'Pack d\'abonnement invalide.')
        return redirect('subscription_packs')

    if request.method == 'POST':
        if request.POST.get('terms'):
            subscription = request.user.subscription
            subscription.pack = pack
            subscription.is_active = True
            subscription.save()

            # Créer une notification pour l'administrateur
            admin_users = CustomUser.objects.filter(role='admin')
            for admin in admin_users:
                Notification.objects.create(
                    user=admin,
                    type='subscription',
                    title='Nouvelle souscription',
                    message=f'L\'utilisateur {request.user.username} a souscrit au {pack.get_name_display()}',
                    related_subscription=subscription
                )

            messages.success(request, 'Votre abonnement a été activé avec succès !')
            return redirect('dashboard_user')
        else:
            messages.error(request, 'Vous devez accepter les conditions d\'utilisation.')

    context = {
        'pack_type': pack_type,
        'pack_name': pack.get_name_display(),
        'pack_price': pack.price
    }
    return render(request, 'core/confirm_subscription.html', context)

@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    messages.success(request, 'Notification marquée comme lue.')
    return redirect('dashboard_user' if not request.user.is_admin() else 'dashboard_admin')
