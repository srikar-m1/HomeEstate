from django.urls import reverse
from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from django.core.files import File
import requests
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_('The email is not given.'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.is_active = False  # Set is_active to False until email is verified
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if not extra_fields.get('is_staff'):
            raise ValueError(_('Superuser must have is_staff = True'))
        if not extra_fields.get('is_superuser'):
            raise ValueError(_('Superuser must have is_superuser = True'))
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser):
    email = models.EmailField(max_length=300, unique=True)
    password = models.CharField(max_length=130, null=False)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)  # Inactive by default until email verified
    email_verified = models.BooleanField(default=False)  # Track email verification
    country_code = models.CharField(max_length=2, null=False)
    mobile_num = models.CharField(
        max_length=10,
        null=False,
        validators=[RegexValidator(regex=r'^\d{10}$', message="Mobile number must be exactly 10 digits.")]
    )
    barcode = models.ImageField(upload_to='images/', blank=True)
    # email_verification_sent_at = models.DateTimeField(null=True, blank=True)  # Add this field

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['country_code', 'mobile_num', 'first_name', 'last_name']

    objects = UserManager()

    def __str__(self):
        return self.email

    def has_module_perms(self, app_label):
        return True

    def has_perm(self, perm, obj=None):
        return True


def shorten_url_with_tinyurl(long_url):
    api_url = f"http://tinyurl.com/api-create.php?url={long_url}"

    try:
        # Send a GET request to the TinyURL API
        response = requests.get(api_url)

        # Raise an exception if the request was unsuccessful (non-2xx status)
        response.raise_for_status()

        # Return the shortened URL
        return response.text.strip()

    except requests.exceptions.RequestException as e:
        print(f"Error shortening URL: {e}")
        return None


@receiver(post_save, sender=CustomUser)
def generate_barcode(sender, instance, created, **kwargs):
    """
    This signal is triggered after a user is saved. It generates a barcode based on the user's ID,
    which contains the shortened URL to the user's details page.
    """
    if created:  # Only generate barcode when a new user is created
        # Generate the full URL to the user's details page
        long_url = reverse('user-details', args=[instance.id])  # Fully qualified URL to user details page
        domain = settings.SITE_URL  # e.g., 'http://localhost:8000' or 'https://yourdomain.com'
        long_url = domain + long_url  # Full URL

        # Shorten the URL using TinyURL
        short_url = shorten_url_with_tinyurl(long_url)

        # Generate the barcode from the shortened URL
        Code128 = barcode.get_barcode_class('code128')

        # Define barcode writer with smaller scaling factors to make it "shorter"
        writer = ImageWriter()
        writer.set_options({
            'module_width': 0.2,  # Adjust the width of each module to reduce the barcode size
            'module_height': 10,  # Set the height to be smaller
            'quiet_zone': 6,  # Quiet zone around the barcode to avoid errors
            'font_size': 8,  # Smaller font size for text (if any)
            'text_distance': 5  # Distance of text from the barcode
        })

        # Create the barcode image using the shortened URL
        code128 = Code128(short_url, writer=writer)  # Use the shortened URL in the barcode
        buffer = BytesIO()
        code128.write(buffer)

        # Save the barcode as an image file
        filename = f'barcode_{instance.email}.png'
        instance.barcode.save(filename, File(buffer), save=False)  # Save the barcode image

        # Save the instance again with the barcode attached
        instance.save()  # This will save the instance with the barcode (avoiding recursion)
