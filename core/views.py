from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from django.utils import timezone
from .models import CustomUser, Subscription, Notification, SubscriptionPack, SupportMessage
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
    
    # Récupérer les notifications de souscription et d'annulation non lues
    subscription_notifications = Notification.objects.filter(
        type__in=['subscription', 'cancellation'],
        is_read=False
    ).order_by('-created_at')

    # Récupérer les messages de support non résolus
    support_messages = SupportMessage.objects.filter(
        is_resolved=False
    ).order_by('-created_at')

    return render(request, 'core/dashboard_admin.html', {
        'total_users': total_users,
        'active_subscriptions': active_subscriptions,
        'recent_users': recent_users,
        'subscription_notifications': subscription_notifications,
        'support_messages': support_messages
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

    if pack_type not in ['simple', 'premium']:
        messages.error(request, 'Type de pack invalide.')
        return redirect('subscription_packs')

    try:
        pack = SubscriptionPack.objects.get(name=pack_type)
    except SubscriptionPack.DoesNotExist:
        messages.error(request, 'Pack d\'abonnement invalide.')
        return redirect('subscription_packs')

    context = {
        'pack': pack,
        'pack_type': pack_type,
        'pack_name': pack.get_name_display(),
        'pack_price': pack.price
    }

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

    return render(request, 'core/confirm_subscription.html', context)

@login_required
def cancel_subscription(request):
    if request.method == 'POST':
        subscription = request.user.subscription
        if subscription.is_active:
            subscription.is_active = False
            subscription.save()

            # Créer une notification pour l'administrateur
            admin_users = CustomUser.objects.filter(role='admin')
            for admin in admin_users:
                Notification.objects.create(
                    user=admin,
                    type='cancellation',
                    title='Annulation d\'abonnement',
                    message=f'L\'utilisateur {request.user.get_full_name() or request.user.username} ({request.user.email}) a annulé son abonnement {subscription.pack.get_name_display()}',
                    related_subscription=subscription
                )

            messages.success(request, 'Votre abonnement a été annulé avec succès.')
        else:
            messages.error(request, 'Vous n\'avez pas d\'abonnement actif à annuler.')
    return redirect('dashboard_user')

@login_required
def send_support_message(request):
    if request.method == 'POST':
        message_content = request.POST.get('message')
        if message_content:
            SupportMessage.objects.create(
                user=request.user,
                message=message_content
            )
            messages.success(request, 'Votre message a été envoyé avec succès à notre équipe de support.')
        else:
            messages.error(request, 'Le message ne peut pas être vide.')
    return redirect('dashboard_user')

@login_required
def resolve_support_message(request, message_id):
    if not request.user.is_admin():
        messages.error(request, 'Accès non autorisé.')
        return redirect('dashboard_user')

    if request.method == 'POST':
        message = get_object_or_404(SupportMessage, id=message_id)
        message.is_resolved = True
        message.save()
        messages.success(request, 'Le message de support a été marqué comme résolu.')
    return redirect('dashboard_admin')

@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)
    if notification.user == request.user or request.user.is_admin():
        notification.is_read = True
        notification.save()
    return redirect(request.user.is_admin() and 'dashboard_admin' or 'dashboard_user')
