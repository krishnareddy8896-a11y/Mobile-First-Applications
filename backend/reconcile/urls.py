from django.urls import path
from .views import disagreement_view

urlpatterns = [
    path("disagreements/", disagreement_view),
]
