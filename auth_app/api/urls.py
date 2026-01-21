from django.urls import path , include
from auth_app.api.views import RegistrationView, LoginView, LogoutView, CookieRefreshView, ActivationView

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='registration'),
    path('activate/<str:uidb64>/<str:token>/', ActivationView.as_view(), name='activation'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', CookieRefreshView.as_view(), name='refresh_token'),
]

