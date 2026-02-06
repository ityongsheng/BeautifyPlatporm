import os
import django
import random
from faker import Faker
from django.utils import timezone

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoBeauty.settings')
django.setup()

from app.models import UserProfile, Product, UserInteraction

fake = Faker(['zh_CN'])

SKIN_TYPES = ['oil', 'dry', 'sensitive', 'combination', 'normal']
CATEGORIES = ['水', '乳', '精华', '面霜', '洁面', '防晒']
INGREDIENTS_POOL = [
    "烟酰胺", "视黄醇", "透明质酸", "胜肽", "神经酰胺", 
    "角鲨烷", "水杨酸", "果酸", "维生素C", "积雪草",
    "虾青素", "泛醇", "咖啡因", "金缕梅", "茶树", "酒精"
]
EFFICACY_POOL = ["保湿", "控油", "美白", "抗衰", "舒缓", "修护", "祛痘", "紧致"]

def create_users(count=1000):
    print(f"Creating {count} users...")
    users = []
    for _ in range(count):
        username = fake.unique.user_name()
        u = UserProfile(
            username=username,
            email=fake.email(),
            skin_type=random.choice(SKIN_TYPES),
            age_group=random.randint(18, 60),
            is_profile_completed=True
        )
        u.set_password('password123')
        users.append(u)
    UserProfile.objects.bulk_create(users)
    print("Users created.")

def create_products(count=2000):
    print(f"Creating {count} products...")
    products = []
    for i in range(count):
        category = random.choice(CATEGORIES)
        brand = fake.company()
        title = f"{brand}{fake.word()}{category}"
        
        # Random ingredients
        ingredients = random.sample(INGREDIENTS_POOL, random.randint(3, 6))
        
        # Random efficacy based on category/ingredients
        efficacy = random.sample(EFFICACY_POOL, random.randint(1, 3))
        
        p = Product(
            title=title,
            brand=brand,
            category=category,
            price=random.randint(50, 2000),
            image_url=f"https://picsum.photos/seed/{i}/200/200",
            ingredients=",".join(ingredients),
            efficacy=",".join(efficacy),
            suitable_skin=random.choice(SKIN_TYPES + ['all']),
            rating_avg=round(random.uniform(3.5, 5.0), 1),
            sales_count=random.randint(0, 10000)
        )
        products.append(p)
    Product.objects.bulk_create(products)
    print("Products created.")

def create_interactions(count=12000):
    print(f"Creating {count} interactions...")
    users = list(UserProfile.objects.all())
    products = list(Product.objects.all())
    types = ['view', 'click', 'fav', 'rate', 'buy']
    
    interactions = []
    seen = set()
    
    batch_size = 2000
    for i in range(count):
        user = random.choice(users)
        product = random.choice(products)
        itype = random.choices(types, weights=[40, 30, 15, 10, 5])[0]
        
        key = (user.id, product.id, itype)
        if key in seen:
            continue
        seen.add(key)
        
        score = 0
        if itype == 'rate':
            score = random.uniform(3.0, 5.0)
        elif itype == 'fav':
            score = 4.0
        elif itype == 'buy':
            score = 5.0
        elif itype == 'click':
            score = 2.0
        else:
            score = 1.0
            
        interactions.append(UserInteraction(
            user=user,
            product=product,
            type=itype,
            score=round(score, 1)
        ))
        
        if len(interactions) >= batch_size:
            UserInteraction.objects.bulk_create(interactions, ignore_conflicts=True)
            interactions = []
            print(f"Progress: {i}/{count}...")

    if interactions:
        UserInteraction.objects.bulk_create(interactions, ignore_conflicts=True)
    print("Interactions created.")

if __name__ == "__main__":
    # Clear existing data if necessary or just append
    # UserProfile.objects.exclude(is_superuser=True).delete()
    # Product.objects.all().delete()
    
    create_users(1000)
    create_products(2000)
    create_interactions(12000)
    print("Data Factory finished successfully!")
