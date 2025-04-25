from django.urls import path
from .views import register_user, login_user, logout_user, user_dashboard
from . import views  # import views


urlpatterns = [
    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('dashboard/', user_dashboard, name='dashboard'),  # ✅ Add dashboard URL
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
]
