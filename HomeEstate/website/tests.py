from unittest.mock import patch

from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import CustomUser
from .models import Favorite, Inquiry, Property
from .tasks import send_inquiry_notification


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    CELERY_TASK_ALWAYS_EAGER=True,
)
class PropertyAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.owner = CustomUser.objects.create_user(
            email='owner@example.com',
            password='strong-pass-123',
            first_name='Owner',
            last_name='User',
            country_code='91',
            mobile_num='9000000001',
        )
        self.visitor = CustomUser.objects.create_user(
            email='visitor@example.com',
            password='strong-pass-123',
            first_name='Visitor',
            last_name='User',
            country_code='91',
            mobile_num='9000000002',
        )
        self.property = Property.objects.create(
            owner=self.owner,
            title='City Apartment',
            description='Two-bedroom apartment near the metro.',
            property_type=Property.PropertyType.APARTMENT,
            listing_type=Property.ListingType.RENT,
            price='35000.00',
            city='Hyderabad',
            address='Gachibowli',
            bedrooms=2,
            bathrooms=2,
            area_sqft=1200,
        )

    def test_public_can_filter_available_properties(self):
        response = self.client.get(reverse('property-list'), {'city': 'hyderabad', 'max_price': '40000'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'City Apartment')

    def test_authenticated_user_can_create_property(self):
        self.client.force_authenticate(self.owner)
        response = self.client.post(
            reverse('property-list'),
            {
                'title': 'Family Villa',
                'description': 'Three-bedroom villa with parking.',
                'property_type': 'villa',
                'listing_type': 'sale',
                'price': '12500000.00',
                'city': 'Hyderabad',
                'address': 'Kokapet',
                'bedrooms': 3,
                'bathrooms': 3,
                'area_sqft': 2400,
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Property.objects.get(title='Family Villa').owner, self.owner)

    def test_only_owner_can_update_property(self):
        self.client.force_authenticate(self.visitor)
        response = self.client.patch(
            reverse('property-detail', args=[self.property.pk]),
            {'price': '30000.00'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_favorite_endpoint_is_idempotent(self):
        self.client.force_authenticate(self.visitor)
        url = reverse('favorite-detail', args=[self.property.pk])

        first = self.client.post(url)
        second = self.client.post(url)

        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second.status_code, status.HTTP_200_OK)
        self.assertEqual(Favorite.objects.filter(user=self.visitor).count(), 1)

    @patch('website.serializers.send_inquiry_notification.delay')
    def test_inquiry_is_visible_to_requester_and_owner(self, delay):
        self.client.force_authenticate(self.visitor)
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(
                reverse('inquiry-list'),
                {'property': self.property.pk, 'message': 'Can I schedule a visit?'},
                format='json',
            )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        inquiry = Inquiry.objects.get()
        delay.assert_called_once_with(inquiry.pk)

        self.client.force_authenticate(self.owner)
        owner_response = self.client.get(reverse('inquiry-list'))
        self.assertEqual(owner_response.data['count'], 1)

    def test_inquiry_task_sends_owner_email(self):
        inquiry = Inquiry.objects.create(
            property=self.property,
            requester=self.visitor,
            message='Please share the available visit times.',
        )

        send_inquiry_notification(inquiry.pk)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.owner.email])
