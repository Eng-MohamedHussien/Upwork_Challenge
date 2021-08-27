from .views import list_units

from django.urls import path

app_name = 'listings'

urlpatterns = [
    path('v1/units/', list_units, name='unit_search'),
]
