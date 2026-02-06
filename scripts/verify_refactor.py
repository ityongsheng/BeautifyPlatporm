import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoBeauty.settings')
django.setup()

from app.recommend_algo import recommend_products
from app.models import UserProfile, Product, UserInteraction
import random

def test_recommendation():
    print("--- Test 1: General Recommendation ---")
    # Pick a random user with some interactions
    user = UserProfile.objects.exclude(is_superuser=True).first()
    if not user:
        print("No users found!")
        return
    
    print(f"Testing for User: {user.username} (Skin Type: {user.skin_type})")
    results = recommend_products(user.id, top_k=5)
    for i, res in enumerate(results):
        print(f"{i+1}. {res['title']} (Score: {res['score']})")
        print(f"   Reason: {res['reason']}")

def test_safety_filter():
    print("\n--- Test 2: Safety Rule (Sensitive Skin + Alcohol) ---")
    sensitive_user = UserProfile.objects.filter(skin_type='sensitive').first()
    if not sensitive_user:
        print("No sensitive user found!")
        return
        
    # Create a product with alcohol to test filtering
    alcohol_prod = Product.objects.create(
        title="Alcohol Test Toner",
        ingredients="水,酒精,香精",
        suitable_skin="oil",
        price=100
    )
    
    print(f"Sensitive User: {sensitive_user.username}")
    results = recommend_products(sensitive_user.id, top_k=20)
    
    titles = [r['title'] for r in results]
    if "Alcohol Test Toner" in titles:
        print("FAIL: Sensitive user received alcohol product!")
    else:
        print("PASS: Alcohol product filtered out for sensitive skin.")
    
    # Cleanup
    alcohol_prod.delete()

if __name__ == "__main__":
    test_recommendation()
    test_safety_filter()
