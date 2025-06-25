from django.urls import path
from . import views

urlpatterns = [
    path('', views.register, name='register'),
    path('dashboard/user/', views.dashboard_user, name='dashboard_user'),
    path('dashboard/admin/', views.dashboard_admin, name='dashboard_admin'),
    path('notification/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('subscription/packs/', views.subscription_packs, name='subscription_packs'),
    path('subscription/confirm/<str:pack_type>/', views.confirm_subscription, name='confirm_subscription'),
]