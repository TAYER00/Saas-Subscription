from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    """Modèle utilisateur personnalisé avec rôle"""
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('user', 'Utilisateur'),
    ]
    
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='user',
        verbose_name='Rôle'
    )
    
    def is_admin(self):
        return self.role == 'admin'

class SubscriptionPack(models.Model):
    """Modèle pour les différents packs d'abonnement"""
    PACK_CHOICES = [
        ('simple', 'Pack Simple'),
        ('premium', 'Pack Premium'),
    ]

    name = models.CharField(max_length=20, choices=PACK_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    features = models.JSONField(default=list)  # Liste des fonctionnalités

    def __str__(self):
        return f'{self.get_name_display()} - {self.price}€'

class Subscription(models.Model):
    """Modèle pour gérer les abonnements"""
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='subscription'
    )
    pack = models.ForeignKey(
        SubscriptionPack,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        pack_name = self.pack.get_name_display() if self.pack else 'Aucun pack'
        return f'Abonnement {pack_name} de {self.user.username}'

class Notification(models.Model):
    """Modèle pour les notifications utilisateur et admin"""
    NOTIFICATION_TYPES = [
        ('subscription', 'Nouvelle souscription'),
        ('cancellation', 'Annulation d\'abonnement'),
        ('support', 'Message support'),
        ('system', 'Notification système'),
        ('user', 'Notification utilisateur'),
    ]

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES,
        default='system'
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    related_subscription = models.ForeignKey(
        Subscription,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications'
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} - {self.user.username}'

class SupportMessage(models.Model):
    """Modèle pour les messages de support"""
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='support_messages'
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Support - {self.user.username} - {self.created_at.strftime("%d/%m/%Y %H:%M")}'

    def save(self, *args, **kwargs):
        # Créer une notification pour les administrateurs lors de la création d'un nouveau message
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
            admin_users = CustomUser.objects.filter(role='admin')
            for admin in admin_users:
                Notification.objects.create(
                    user=admin,
                    type='support',
                    title='Nouveau message support',
                    message=f'Message de {self.user.get_full_name() or self.user.username} : {self.message[:100]}...',
                )
