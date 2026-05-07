from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .services import GroqChatbot, FakeNewsDetector, SentimentAnalyzer
from .models import ChatMessage, FakeNewsAnalysis, SentimentAnalysis


chatbot = GroqChatbot()
fake_news_detector = FakeNewsDetector()
sentiment_analyzer = SentimentAnalyzer()


@login_required
def chatbot_view(request):
    if request.method == 'POST':
        message = request.POST.get('message')

        # Get conversation history
        history = ChatMessage.objects.filter(user=request.user).order_by('-timestamp')[:10]
        context = []
        for msg in reversed(history):
            context.append({"role": "user", "content": msg.message})
            context.append({"role": "assistant", "content": msg.response})

        response = chatbot.chat(message, context)

        # Save to database
        ChatMessage.objects.create(
            user=request.user,
            message=message,
            response=response
        )

        return JsonResponse({'response': response})

    chat_history = ChatMessage.objects.filter(user=request.user).order_by('-timestamp')[:20]
    return render(request, 'ai_services/chatbot.html', {'chat_history': chat_history})


@login_required
def clear_chat(request):
    """Clear all chat history for the current user."""
    if request.method == 'POST':
        ChatMessage.objects.filter(user=request.user).delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'POST request required'})


@csrf_exempt
def detect_fake_news(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        url = data.get('url', '')
        title = data.get('title', '')
        content = data.get('content', '')
        
        text_to_analyze = f"{title} {content}"
        result = fake_news_detector.analyze(text_to_analyze)
        
        # Save analysis
        analysis = FakeNewsAnalysis.objects.create(
            url=url,
            title=title,
            content=content,
            is_fake=result.get('is_fake'),
            confidence_score=result.get('confidence')
        )
        
        return JsonResponse({
            'is_fake': result.get('is_fake'),
            'confidence': result.get('confidence'),
            'error': result.get('error')
        })
    
    return JsonResponse({'error': 'POST request required'})


@login_required
def analyze_sentiment(request):
    if request.method == 'POST':
        text = request.POST.get('text')
        result = sentiment_analyzer.analyze(text)
        
        # Save analysis
        SentimentAnalysis.objects.create(
            user=request.user,
            text=text,
            sentiment=result.get('sentiment'),
            confidence=result.get('confidence')
        )
        
        return JsonResponse({
            'sentiment': result.get('sentiment'),
            'confidence': result.get('confidence')
        })
    
    return render(request, 'ai_services/sentiment_analysis.html')
