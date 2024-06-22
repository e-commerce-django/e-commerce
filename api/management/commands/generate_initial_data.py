import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from products.models import Product
from api.models import UserAction

User = get_user_model()

class Command(BaseCommand):
    help = 'Generate initial user action data for simulation'

    def handle(self, *args, **kwargs):
        users = User.objects.all()
        products = Product.objects.all()
        actions = ['view', 'like', 'bid']

        for _ in range(1000):  # 원하는 만큼 데이터 생성
            user = random.choice(users)
            product = random.choice(products)
            action_type = random.choice(actions)
            UserAction.objects.create(user=user, product=product, action_type=action_type)

        self.stdout.write(self.style.SUCCESS('Successfully generated initial user action data'))
