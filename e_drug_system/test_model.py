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
    test_text = """Drug addiction is a chronic disorder that affects both the brain and behavior.
Medical experts emphasize that recovery requires structured treatment plans, including detoxification, therapy, and continuous support from trained professionals."""
    result = detector.analyze(test_text)
    print(f"Test result: {result}")
else:
    print("✗ Model failed to load")
