import random
from faker import Faker
from app.models import UserProfile, Product, UserInteraction
from django.db import transaction

fake = Faker(['zh_CN'])
SKIN_TYPES = ['oil', 'dry', 'sensitive', 'combination', 'normal']
CATEGORIES = ['水', '乳', '精华', '面霜', '洁面', '防晒']
INGREDIENTS_POOL = ["烟酰胺", "视黄醇", "透明质酸", "胜肽", "神经酰胺", "角鲨烷", "水杨酸", "果酸", "维生素C", "积雪草"]

def run():
    with transaction.atomic():
        print("Generating 1000 users...")
        users = [
            UserProfile(
                username=fake.unique.user_name(),
                email=fake.email(),
                skin_type=random.choice(SKIN_TYPES),
                age_group=random.randint(18, 60),
                is_profile_completed=True
            ) for _ in range(1000)
        ]
        for u in users: u.set_password('password123')
        UserProfile.objects.bulk_create(users)

        print("Generating 2000 products...")
        products = [
            Product(
                title=f"{fake.company()}{fake.word()}{random.choice(CATEGORIES)}",
                brand=fake.company(),
                category=random.choice(CATEGORIES),
                price=random.randint(50, 1500),
                ingredients=",".join(random.sample(INGREDIENTS_POOL, 3)),
                efficacy="保湿,控油",
                suitable_skin=random.choice(SKIN_TYPES),
                rating_avg=random.uniform(3.5, 5.0),
                sales_count=random.randint(0, 5000)
            ) for i in range(2000)
        ]
        Product.objects.bulk_create(products)

    print("Generating 12000 interactions...")
    all_users = list(UserProfile.objects.all())
    all_products = list(Product.objects.all())
    
    # Generate interactions in batches to avoid memory issues
    batch_size = 1000
    for i in range(0, 12000, batch_size):
        interactions = []
        for _ in range(batch_size):
            u = random.choice(all_users)
            p = random.choice(all_products)
            t = random.choice(['view', 'click', 'fav', 'rate', 'buy'])
            interactions.append(UserInteraction(user=u, product=p, type=t, score=random.uniform(1, 5)))
        UserInteraction.objects.bulk_create(interactions, ignore_conflicts=True)
        print(f"Batch {i//batch_size + 1} done.")

run()
