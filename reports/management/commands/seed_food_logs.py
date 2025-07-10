import random
from datetime import date, timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from faker import Faker

from reports.models import FoodLog

fake = Faker()

CATEGORIES = ["fruit", "vegetable", "dairy", "protein", "snack"]
FOOD_NAMES = {
    "fruit": ["Apple", "Banana", "Orange", "Grapes"],
    "vegetable": ["Carrot", "Tomato", "Spinach", "Cucumber"],
    "dairy": ["Milk", "Cheese", "Yogurt"],
    "protein": ["Chicken", "Beef", "Tofu", "Eggs"],
    "snack": ["Chips", "Chocolate", "Cookies"],
}


class Command(BaseCommand):
    help = "Generate fake users and food logs"

    def add_arguments(self, parser):
        parser.add_argument("--users", type=int, default=10)
        parser.add_argument("--logs", type=int, default=1000)

    def handle(self, *args, **options):
        user_count = options["users"]
        log_count = options["logs"]

        self.stdout.write(f"Creating {user_count} users...")
        users = []
        for _ in range(user_count):
            users.append(
                User(
                    username=fake.user_name(),
                    email=fake.email(),
                    password="password123",
                )
            )

        User.objects.bulk_create(users, batch_size=500)
        self.stdout.write(f"Creating {log_count} food logs...")

        food_logs = []
        for _ in range(log_count):
            category = random.choice(CATEGORIES)
            food_name = random.choice(FOOD_NAMES[category])
            user = random.choice(users)
            log_date = date.today() - timedelta(days=random.randint(0, 60))

            food_logs.append(
                FoodLog(
                    user=user,
                    food_name=food_name,
                    category=category,
                    date_logged=log_date,
                )
            )
        FoodLog.objects.bulk_create(food_logs, batch_size=500)
        self.stdout.write(self.style.SUCCESS("✅ Fake data generated successfully!"))
