from django.urls import path
from . import views

urlpatterns = [
    path('tenders/', views.read_tenders),
    path('tenders/<str:tender_id>', views.read_tender),
    path('notifications/', views.read_notifications),
]
