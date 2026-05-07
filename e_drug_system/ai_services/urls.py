from django.urls import path
from . import views

urlpatterns = [
    path('chatbot/', views.chatbot_view, name='chatbot'),
    path('chatbot/clear/', views.clear_chat, name='clear_chat'),
    path('fake-news/', views.detect_fake_news, name='detect_fake_news'),
    path('sentiment/', views.analyze_sentiment, name='analyze_sentiment'),
]
