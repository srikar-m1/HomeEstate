from django.db import transaction
from rest_framework import serializers

from .models import Favorite, Inquiry, Property
from .tasks import send_inquiry_notification


class PropertySerializer(serializers.ModelSerializer):
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    is_favorite = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = (
            'id',
            'owner_email',
            'title',
            'description',
            'property_type',
            'listing_type',
            'price',
            'city',
            'address',
            'bedrooms',
            'bathrooms',
            'area_sqft',
            'is_available',
            'is_favorite',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('owner_email', 'created_at', 'updated_at')

    def get_is_favorite(self, obj) -> bool:
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.favorites.filter(user=request.user).exists()


class FavoriteSerializer(serializers.ModelSerializer):
    property = PropertySerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ('id', 'property', 'created_at')


class InquirySerializer(serializers.ModelSerializer):
    requester_email = serializers.EmailField(source='requester.email', read_only=True)
    property_title = serializers.CharField(source='property.title', read_only=True)

    class Meta:
        model = Inquiry
        fields = (
            'id',
            'property',
            'property_title',
            'requester_email',
            'message',
            'status',
            'created_at',
        )
        read_only_fields = ('requester_email', 'property_title', 'status', 'created_at')

    def create(self, validated_data):
        inquiry = Inquiry.objects.create(
            requester=self.context['request'].user,
            **validated_data,
        )
        transaction.on_commit(lambda: send_inquiry_notification.delay(inquiry.pk))
        return inquiry
