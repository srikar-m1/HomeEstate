from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name="index"),
    path('api/properties/', views.PropertyListCreateAPIView.as_view(), name='property-list'),
    path('api/properties/<int:pk>/', views.PropertyDetailAPIView.as_view(), name='property-detail'),
    path('api/favorites/', views.FavoriteListAPIView.as_view(), name='favorite-list'),
    path('api/favorites/<int:property_id>/', views.FavoriteDetailAPIView.as_view(), name='favorite-detail'),
    path('api/inquiries/', views.InquiryListCreateAPIView.as_view(), name='inquiry-list'),
   ]
