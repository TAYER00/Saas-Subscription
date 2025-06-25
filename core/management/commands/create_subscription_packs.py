from django.core.management.base import BaseCommand
from core.models import SubscriptionPack

class Command(BaseCommand):
    help = 'Create initial subscription packs'

    def handle(self, *args, **kwargs):
        # Supprimer les packs existants pour éviter les doublons
        SubscriptionPack.objects.all().delete()

        # Créer le Pack Simple
        SubscriptionPack.objects.create(
            name='simple',
            price=29.99,
            description='Pack de base avec les fonctionnalités essentielles',
            features=[
                'Accès aux fonctionnalités de base',
                'Support par email',
                'Mises à jour mensuelles'
            ]
        )

        # Créer le Pack Premium
        SubscriptionPack.objects.create(
            name='premium',
            price=99.99,
            description='Pack premium avec toutes les fonctionnalités avancées',
            features=[
                'Toutes les fonctionnalités du pack simple',
                'Fonctionnalités avancées',
                'Support prioritaire 24/7',
                'Mises à jour hebdomadaires',
                'Accès aux fonctionnalités beta'
            ]
        )

        self.stdout.write(
            self.style.SUCCESS('Les packs d\'abonnement ont été créés avec succès !')
        )