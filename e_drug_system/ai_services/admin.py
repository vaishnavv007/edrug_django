from django.contrib import admin
from .models import ChatMessage, FakeNewsAnalysis, SentimentAnalysis


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['user', 'timestamp']
    search_fields = ['user__username', 'message']
    list_filter = ['timestamp']
    readonly_fields = ['timestamp']


@admin.register(FakeNewsAnalysis)
class FakeNewsAnalysisAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_fake', 'confidence_score', 'analyzed_at']
    search_fields = ['title', 'url']
    list_filter = ['is_fake', 'analyzed_at']
    readonly_fields = ['analyzed_at']


@admin.register(SentimentAnalysis)
class SentimentAnalysisAdmin(admin.ModelAdmin):
    list_display = ['user', 'sentiment', 'confidence', 'analyzed_at']
    search_fields = ['user__username', 'text']
    list_filter = ['sentiment', 'analyzed_at']
    readonly_fields = ['analyzed_at']
