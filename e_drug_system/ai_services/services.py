import os
import pickle
import numpy as np
from typing import List, Dict
from django.conf import settings
import faiss
from transformers import pipeline, AutoTokenizer, AutoModel
import requests
import torch


class GroqChatbot:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.api_url = "https://api.groq.com/openai/v1"
    
    def chat(self, message: str, context: List[Dict] = None) -> str:
        if not self.api_key:
            return "Groq API key not configured. Please set GROQ_API_KEY in .env file."
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        system_prompt = """
You are a supportive and understanding AI assistant for an E-Drug awareness and rehabilitation support system.

Talk like a real person having a calm, caring conversation. Your responses should feel natural, human, and easy to understand — not robotic, overly formal, or textbook-like.

Guidelines for your responses:
- Use a warm, empathetic, and respectful tone
- Explain things in simple everyday language
- Sound conversational and supportive
- Avoid overly technical or clinical wording unless necessary
- Keep responses balanced, realistic, and non-judgmental
- Show understanding without sounding dramatic or fake
- Use short paragraphs for readability
- Use simple numbered lists only when helpful
- Avoid sounding repetitive or scripted
- Encourage seeking professional help when appropriate

Formatting rules:
- Use plain text only
- Do NOT use markdown formatting
- Do NOT use asterisks (*), underscores (_), hashtags (#), or backticks
- Do NOT use markdown tables
- Keep headings simple and clean
- Separate ideas with blank lines

Important:
- Never shame, insult, or guilt the user
- Avoid fear-based responses
- Do not pretend to be a doctor or therapist
- If the topic involves addiction, mental health, overdose, or recovery, respond with compassion and practical guidance

Always include this disclaimer naturally at the end of the response:

"This information is for general awareness and support only. I'm not a medical professional, so it's important to speak with a qualified doctor, therapist, or addiction counselor for personal advice and treatment."

Your goal is to make the user feel informed, understood, and comfortable asking questions.
"""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        if context:
            messages.extend(context)
        
        messages.append({"role": "user", "content": message})
        
        try:
            response = requests.post(
                f"{self.api_url}/chat/completions",
                headers=headers,
                json={
                    "messages": messages,
                    "model": "openai/gpt-oss-20b",
                    "temperature": 0.7,
                    "max_tokens": 1024
                }
            )
            response.raise_for_status()
            data = response.json()
            response_text = data['choices'][0]['message']['content']
            # Strip markdown formatting
            response_text = self._strip_markdown(response_text)
            return response_text
        except Exception as e:
            return f"Error communicating with Groq API: {str(e)}"
    
    def _strip_markdown(self, text: str) -> str:
        """Remove markdown formatting from text."""
        import re
        # Remove bold formatting (**text**)
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        # Remove italic formatting (*text*)
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        # Remove headers (# text)
        text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
        # Remove code blocks (```text```)
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        # Remove inline code (`text`)
        text = re.sub(r'`(.*?)`', r'\1', text)
        # Remove horizontal rules (--- or ***)
        text = re.sub(r'^[-*]{3,}$', '', text, flags=re.MULTILINE)
        return text


class FAISSVectorSearch:
    def __init__(self):
        self.index_path = os.path.join(settings.BASE_DIR, 'faiss_index_archive')
        self.dimension = 768  # BERT base dimension
        self.index = None
        self.documents = []
        self.tokenizer = None
        self.model = None
        self._load_or_create_index()
        self._load_bert_model()
    
    def _load_or_create_index(self):
        index_file = os.path.join(self.index_path, "index.faiss")
        pkl_file = os.path.join(self.index_path, "index.pkl")
        
        if os.path.exists(index_file):
            self.index = faiss.read_index(index_file)
        else:
            self.index = faiss.IndexFlatL2(self.dimension)
            self._save_index()
        
        # Load documents from pickle file
        if os.path.exists(pkl_file):
            try:
                with open(pkl_file, 'rb') as f:
                    self.documents = pickle.load(f)
            except Exception as e:
                print(f"Error loading documents from pickle: {e}")
                self.documents = []
    
    def _load_bert_model(self):
        try:
            model_name = getattr(settings, 'BERT_MODEL_NAME', 'bert-base-uncased')
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModel.from_pretrained(model_name)
        except Exception as e:
            print(f"Error loading BERT model: {e}")
    
    def _save_index(self):
        index_file = os.path.join(self.index_path, "index.faiss")
        faiss.write_index(self.index, index_file)
    
    def get_embedding(self, text: str) -> np.ndarray:
        """Generate BERT embedding for a given text."""
        if self.tokenizer is None or self.model is None:
            # Return zero embedding if model not loaded
            return np.zeros(self.dimension)
        
        try:
            inputs = self.tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
            with torch.no_grad():
                outputs = self.model(**inputs)
            # Use mean pooling of the last hidden state
            embedding = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
            return embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return np.zeros(self.dimension)
    
    def add_document(self, text: str, embedding: np.ndarray):
        self.index.add(embedding.reshape(1, -1))
        self.documents.append(text)
        self._save_index()
    
    def search(self, query_embedding: np.ndarray, k: int = 5) -> List[tuple]:
        if self.index.ntotal == 0:
            return []
        
        distances, indices = self.index.search(query_embedding.reshape(1, -1), k)
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.documents):
                results.append((self.documents[idx], float(dist)))
        return results
    
    def search_by_text(self, query_text: str, k: int = 5) -> List[tuple]:
        """Search using text query by generating embedding first."""
        query_embedding = self.get_embedding(query_text)
        return self.search(query_embedding, k)


class FakeNewsDetector:
    def __init__(self):
        self.model_path = os.path.join(settings.BASE_DIR, 'fake_news_bert_model')
        try:
            self.classifier = pipeline(
                "text-classification",
                model=self.model_path,
                tokenizer=self.model_path
            )
        except Exception as e:
            print(f"Error loading BERT model: {e}")
            self.classifier = None
    
    def analyze(self, text: str) -> Dict:
        if self.classifier is None:
            return {
                "is_fake": None,
                "confidence": 0.0,
                "error": "Model not loaded"
            }
        
        try:
            result = self.classifier(text)[0]
            # Model outputs LABEL_0 (fake) or LABEL_1 (real)
            # This model is trained with opposite convention
            is_fake = result['label'] == 'LABEL_0'
            confidence = result['score']
            
            return {
                "is_fake": is_fake,
                "confidence": confidence,
                "label": result['label']
            }
        except Exception as e:
            return {
                "is_fake": None,
                "confidence": 0.0,
                "error": str(e)
            }


class SentimentAnalyzer:
    def __init__(self):
        try:
            self.classifier = pipeline("sentiment-analysis")
        except Exception as e:
            print(f"Error loading sentiment model: {e}")
            self.classifier = None
    
    def analyze(self, text: str) -> Dict:
        if self.classifier is None:
            return {
                "sentiment": "NEUTRAL",
                "confidence": 0.0,
                "error": "Model not loaded"
            }
        
        try:
            result = self.classifier(text)[0]
            return {
                "sentiment": result['label'],
                "confidence": result['score']
            }
        except Exception as e:
            return {
                "sentiment": "NEUTRAL",
                "confidence": 0.0,
                "error": str(e)
            }
