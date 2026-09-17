from django.urls import path
from . import views

urlpatterns = [
    # Registration page and API endpoint for registration
    path('register/', views.register_view, name='register'),  # Renders the register.html
    path('api/register/', views.CreateUser.as_view(), name='register-api'),  # POST to handle registration

    # Login view and API endpoint for login
    path('login/', views.login_view, name='login'),  # This URL serves the login form (GET)
    path('api/login/', views.Login.as_view(), name='login-api'),  # POST to handle login

    # Logout for the current session (invalidate token)
    path('api/logout/', views.CustomLogoutView.as_view(), name='logout-api'),  # POST to logout with token

    # Logout from all sessions (invalidate all tokens) using Knox
    path('logoutAll/', views.LogoutAll.as_view(), name='logout-all-api'),

    # User profile update
    path('api/update/<int:pk>/', views.UpdateUser.as_view(), name='update-user'),
    path('update/', views.updateform, name='update-user-form'),  # Update user details

    # User details page (show user details)
    path('user-details/<int:user_id>/', views.user_details, name='user-details'),

    path('verify-email/<uidb64>/<token>/', views.verify_email, name='verify_email'),

    path('email-verified/', views.email_verified_success, name='email_verified_success')


]
