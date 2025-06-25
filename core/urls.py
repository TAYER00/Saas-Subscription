from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('dashboard/user/', views.dashboard_user, name='dashboard_user'),
    path('dashboard/admin/', views.dashboard_admin, name='dashboard_admin'),
    path('subscription/packs/', views.subscription_packs, name='subscription_packs'),
    path('subscription/confirm/<str:pack_type>/', views.confirm_subscription, name='confirm_subscription'),
    path('subscription/cancel/', views.cancel_subscription, name='cancel_subscription'),
    path('support/send/', views.send_support_message, name='send_support_message'),
    path('support/resolve/<int:message_id>/', views.resolve_support_message, name='resolve_support_message'),
    path('notification/read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
]