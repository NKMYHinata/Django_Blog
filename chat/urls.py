from django.urls import path
from .views import IndexView

urlpatterns = [
    path('gpt/', IndexView.as_view(), name='chat'),
]
