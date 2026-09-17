from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Favorite, Inquiry, Property
from .permissions import IsOwnerOrReadOnly
from .serializers import FavoriteSerializer, InquirySerializer, PropertySerializer


def index(request):
    return render(request, 'index.html')  # Render a basic home template


@method_decorator(cache_page(60), name='get')
class PropertyListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = PropertySerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        queryset = Property.objects.select_related('owner').filter(is_available=True)
        params = self.request.query_params
        search = params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(description__icontains=search)
                | Q(city__icontains=search)
            )
        for field in ('city', 'listing_type', 'property_type'):
            if params.get(field):
                queryset = queryset.filter(**{f'{field}__iexact': params[field]})
        if params.get('min_price'):
            queryset = queryset.filter(price__gte=params['min_price'])
        if params.get('max_price'):
            queryset = queryset.filter(price__lte=params['max_price'])
        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class PropertyDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Property.objects.select_related('owner')
    serializer_class = PropertySerializer
    permission_classes = (IsOwnerOrReadOnly,)


class FavoriteListAPIView(generics.ListAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user).select_related('property', 'property__owner')


@extend_schema_view(
    post=extend_schema(request=None, responses=FavoriteSerializer),
    delete=extend_schema(request=None, responses={204: None}),
)
class FavoriteDetailAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = FavoriteSerializer

    def post(self, request, property_id):
        property_obj = get_object_or_404(Property, pk=property_id, is_available=True)
        favorite, created = Favorite.objects.get_or_create(user=request.user, property=property_obj)
        response_status = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(FavoriteSerializer(favorite, context={'request': request}).data, status=response_status)

    def delete(self, request, property_id):
        favorite = get_object_or_404(Favorite, user=request.user, property_id=property_id)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class InquiryListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = InquirySerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Inquiry.objects.filter(
            Q(requester=self.request.user) | Q(property__owner=self.request.user)
        ).select_related('requester', 'property').distinct()
