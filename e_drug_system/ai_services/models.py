from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages')
    message = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username} - {self.timestamp}"


class FakeNewsAnalysis(models.Model):
    url = models.URLField()
    title = models.TextField()
    content = models.TextField()
    is_fake = models.BooleanField(null=True)
    confidence_score = models.FloatField(null=True)
    analyzed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-analyzed_at']

    def __str__(self):
        return f"{self.title[:50]}... - {'FAKE' if self.is_fake else 'REAL'}"


class SentimentAnalysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sentiment_analyses')
    text = models.TextField()
    sentiment = models.CharField(max_length=20)
    confidence = models.FloatField()
    analyzed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-analyzed_at']

    def __str__(self):
        return f"{self.user.username} - {self.sentiment}"
