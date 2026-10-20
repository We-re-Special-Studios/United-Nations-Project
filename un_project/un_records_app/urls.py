from django.urls import path, include
from .views import *

urlpatterns = [
    path('records-home', records_home, name='records_home'),
    path('charter', charter, name='charter'),
    path('resolutions', resolutions, name='resolutions'),
    path('resolutions/<slug:slug>/', resolution_detail, name='resolution_detail'),
    path('court-cases', court_cases, name='court_cases'),
    path('court-cases/<slug:slug>/', court_case_detail, name='court_case_detail'),
    path('treaties', treaties, name='treaties'),
    path('treaties/<slug:slug>/', treaty_detail, name='treaty_detail'),
    path('executive_orders', executive_orders, name='executive_orders'),
    path('executive-orders/<int:charter>/<int:number>/', executive_order_detail, name='executive_order_detail'),
    path('alliances', alliances, name='alliances'),
    path('declaration_of_wars', declaration_of_wars, name='declaration_of_wars'),
    path('national_constitution', national_constitutions, name='national_constitution'),
    path('aternos_games', aternos_games, name='aternos_games'),
    path('petitions', petitions, name='petitions'),
    path('un-staff', un_staff, name='un_staff'),
]