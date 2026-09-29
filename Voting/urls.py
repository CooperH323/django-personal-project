from django.urls import path

from .views import *

urlpatterns = [
    path('', PetList.as_view(), name ='home'),
    path('pets/<int:pk>/', PetDetail.as_view(), name= 'pet_detail'),
    path('pet/new', PetCreateView.as_view(), name='pet_new'),
    path('post/<int:pk>/edit', PetUpdateView.as_view(), name='pet_edit'),
    path('pet/<int:pk>/delete', PetDeleteView.as_view(), name='pet_delete'),
]
