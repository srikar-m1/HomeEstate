# from datetime import timedelta
# from django.utils import timezone
from django.contrib.auth import login, logout
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from knox import views as knox_views
from knox.models import AuthToken
from .models import CustomUser
from .serializers import CreateUserSerializer, UpdateUserSerializer, LoginSerializer
from django.urls import reverse


# View to render the registration page (GET request)
def register_view(request):
    if request.method == 'POST':
        try:
            # Registration logic
            user = CustomUser.objects.create_user(**request.POST)  # Example logic, update as needed
            user.send_verification_email(request)
            return render(request, 'register.html', {
                'alert_message': 'Registration successful! Please check your email to verify your account.',
                'alert_type': 'success',  # You can choose 'success' or 'error' based on the situation
            })
        except Exception as e:
            return render(request, 'register.html', {
                'alert_message': f'Error: {str(e)}',
                'alert_type': 'error',
            })

    return render(request, 'register.html', {'user': request.user})


class CreateUser(CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CreateUserSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 201:
            # Access the created user
            user = CustomUser.objects.get(email=request.data.get('email'))
            print(f"Request is being passed: {request}")

            # Send the verification email
            self.send_verification_email(user, request)

            return redirect('login')  # After successful registration, redirect to login page

        return Response(response.data, status=status.HTTP_400_BAD_REQUEST)

    def send_verification_email(self, user, request):
        """
        This function handles the email verification process for a newly created user.
        """
        # Generate the token
        token = default_token_generator.make_token(user)

        # Encode the user's ID
        uid = urlsafe_base64_encode(str(user.pk).encode())  # Encode user ID

        # Create the verification URL
        verification_link = reverse('verify_email', kwargs={'uidb64': uid, 'token': token})

        # Get the current domain
        domain = get_current_site(request).domain

        # Complete URL for email verification
        full_verification_url = f"http://{domain}{verification_link}"

        # Send the email
        send_mail(
            'Please verify your email address',
            f'Click the link below to verify your email address:\n\n{full_verification_url}',
            'no-reply@yourwebsite.com',
            [user.email],
            fail_silently=False,
        )


# This view should be outside the CreateUser class.
def verify_email(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()  # Decode the uid from the URL
        user = get_object_or_404(CustomUser, pk=uid)  # Get the user object

        # Check if the token is valid
        if default_token_generator.check_token(user, token):
            # Set the user's email_verified and is_active status
            user.email_verified = True
            user.is_active = True
            user.save()

            # Redirect the user to the login page after successful verification
            return HttpResponseRedirect('email-verified/')

        else:
            return HttpResponse("Invalid token.")

    except Exception as e:
        return HttpResponse(f"Error: {str(e)}")


def updateform(request):
    return render(request, "update.html")


# View to handle user profile updates
class UpdateUser(UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UpdateUserSerializer
    permission_classes = (IsAuthenticated,)  # Only authenticated users can update their profile

    def perform_update(self, request, serializer, pk=None):
        # Save the updated user information
        user = CustomUser.objects.get(id=pk)
        if user != request.user:
            return Response({"detail": "You cannot update another user's profile."}, status=403)

        serializer = UpdateUserSerializer(user, data=request.data, partial=True)

        user = serializer.save()

        # You can perform additional logic if needed before redirecting
        return super().perform_update(serializer)

    def get_success_url(self):
        # Redirect to the home page after a successful update
        return '/'


def login_view(request):
    return render(request, 'login.html')


# View to handle login with Knox token
class Login(knox_views.LoginView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data['user']

            # Check if email is verified before logging in
            if not user.email_verified:
                return Response({'errors': 'Please verify your email address first.'},
                                status=status.HTTP_400_BAD_REQUEST)

            token = AuthToken.objects.create(user)[1]  # Knox token

            # Log the user into Django session
            login(request, user)

            # Prepare the response data
            response_data = {
                'user': {
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                },
                'token': token
            }

            # Return JSON response with the token and user data
            # Redirect to home page after successful login
            response = Response(response_data, status=status.HTTP_200_OK)
            response['Location'] = '/'  # Redirect to home page

            return response

        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


# User details view
def user_details(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)
    return render(request, 'user_details.html', {'user': user})


# User logout view (invalidate current token)
class CustomLogoutView(knox_views.LogoutView):
    permission_classes = [IsAuthenticated]  # Only authenticated users can logout

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        logout(request)
        # Redirect to the home page after logout
        return redirect('/')


# User logout all view using Knox (invalidate all tokens)
class LogoutAll(knox_views.LogoutAllView):
    permission_classes = (IsAuthenticated,)


def email_verified_success(request):
    return render(request, 'email_success.html')  # A simple success page
