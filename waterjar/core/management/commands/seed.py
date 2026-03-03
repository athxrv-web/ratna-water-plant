from django.core.management.base import BaseCommand
from core.models import User


class Command(BaseCommand):
    help = "Create initial owner and sample staff accounts for Ratna Water Plant"

    def handle(self, *args, **options):
        # Create Owner
        if not User.objects.filter(username="owner").exists():
            User.objects.create_superuser(
                username="owner",
                password="owner123",
                first_name="mahendra",
                last_name="tripathi",
                role=User.Role.OWNER,
                email="owner@ratnawater@gmail.com",
            )
            self.stdout.write(
                self.style.SUCCESS("✓ Owner created  →  username: owner  |  password: owner123")
            )
        else:
            self.stdout.write("  Owner already exists, skipping.")

        # Create sample Staff
        if not User.objects.filter(username="staff1").exists():
            User.objects.create_user(
                username="staff1",
                password="staff123",
                first_name="Ravi",
                last_name="Kumar",
                role=User.Role.STAFF,
                phone="9876543210",
            )
            self.stdout.write(
                self.style.SUCCESS("✓ Staff created   →  username: staff1  |  password: staff123")
            )
        else:
            self.stdout.write("  staff1 already exists, skipping.")

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Setup complete! Run: python manage.py runserver"))