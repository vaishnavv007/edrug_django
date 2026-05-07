# E-Drug: AI-Powered Drug Awareness & Rehabilitation Support System

## Project Overview
E-Drug is a Django-based web application that provides drug awareness information, rehabilitation resources, and AI-powered support for individuals seeking help with substance abuse.

## Tech Stack
- **Backend**: Django 4.2.7 (Python 3.11)
- **Frontend**: HTML, CSS, JavaScript (no React)
- **Database**: SQLite (initial setup)
- **AI Services**:
  - FAISS for vector search
  - Groq API for chatbot (RAG)
  - BERT for fake news detection
  - Sentiment analysis

## User Roles
1. **Anonymous User**: Can browse public information
2. **Registered User**: Full access to features
3. **Admin**: Full system administration
4. **Moderator**: Content moderation
5. **Healthcare Expert**: Verified professional access

## Setup Instructions

### 1. Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env` and fill in your API keys:
```bash
copy .env.example .env
```

Edit `.env` with your actual values:
- `SECRET_KEY`: Generate a secure secret key for Django
- `GROQ_API_KEY`: Your Groq API key for the chatbot
- Other settings can be left as defaults for development

### 4. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser
```bash
python manage.py createsuperuser
```

### 6. Run Development Server
```bash
python manage.py runserver
```

Access the application at `http://localhost:8000`

## Features

### Core Features
- **Drug Information**: Comprehensive database of drugs with effects and risks
- **Rehabilitation Centers**: Directory of verified treatment centers
- **Support Groups**: Find and join recovery support groups
- **Educational Resources**: Articles, videos, and guides

### AI Features
- **AI Chatbot**: RAG-powered assistant for drug awareness queries
- **Fake News Detection**: BERT-based analysis of drug-related news
- **Sentiment Analysis**: Analyze user sentiment in support contexts

### User Features
- User registration and authentication
- Role-based access control
- Profile management
- Dashboard with personalized content

## Project Structure
```
e_drug_system/
├── e_drug_system/          # Main Django project
│   ├── settings.py         # Project settings
│   ├── urls.py            # Main URL routing
│   └── wsgi.py            # WSGI configuration
├── core/                   # Core app (drugs, centers, groups)
├── users/                  # User authentication and profiles
├── ai_services/            # AI-powered features
├── templates/              # HTML templates
├── static/                 # CSS, JS, images
├── media/                  # User uploads
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
└── .env.example           # Environment variables template
```

## API Keys Required
- **Groq API Key**: For the AI chatbot feature
  - Get it from: https://console.groq.com/

## Development Notes
- Python 3.11 is recommended
- Virtual environment is required
- SQLite is used by default (can be switched to PostgreSQL for production)
- Static files and media are served locally in development

## Security Notes
- Never commit `.env` file with real API keys
- Change `SECRET_KEY` in production
- Enable HTTPS and security settings in production
- Review and update `ALLOWED_HOSTS` for production

## License
This project is for educational and awareness purposes.
