from django.urls import reverse
from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from django.core.files import File
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from urllib.parse import urljoin


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
    password = models.CharField(max_length=130, null=True)
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


@receiver(post_save, sender=CustomUser)
def generate_barcode(sender, instance, created, **kwargs):
    if not created:
        return

    profile_path = reverse('user-details', args=[instance.id])
    profile_url = urljoin(f"{settings.SITE_URL.rstrip('/')}/", profile_path.lstrip('/'))
    code128 = barcode.get_barcode_class('code128')(profile_url, writer=ImageWriter())
    buffer = BytesIO()
    code128.write(buffer)
    instance.barcode.save(
        f'barcode_{instance.pk}.png',
        File(buffer),
        save=False,
    )
    instance.save(update_fields=['barcode'])
