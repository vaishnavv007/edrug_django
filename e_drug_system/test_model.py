import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'e_drug_system.settings')
django.setup()

from ai_services.services import FakeNewsDetector

print("Testing FakeNewsDetector model loading...")
detector = FakeNewsDetector()

if detector.classifier:
    print("✓ Model loaded successfully!")
    
    # Test with sample text
    test_text = "This is a test news article about drugs"
    result = detector.analyze(test_text)
    print(f"Test result: {result}")
else:
    print("✗ Model failed to load")
