from django.core.management.base import BaseCommand
from waterjar.core.models import User


class Command(BaseCommand):
    help = "Create initial owner and staff accounts"

    def handle(self, *args, **options):
        if not User.objects.filter(username="owner").exists():
            User.objects.create_superuser(
                username="owner", password="owner123",
                first_name="Ratna", last_name="Owner",
                role=User.Role.OWNER, email="owner@ratnawater.local",
            )
            self.stdout.write(self.style.SUCCESS("Owner created: owner / owner123"))

        if not User.objects.filter(username="staff1").exists():
            User.objects.create_user(
                username="staff1", password="staff123",
                first_name="Ravi", last_name="Kumar",
                role=User.Role.STAFF, phone="9876543210",
            )
            self.stdout.write(self.style.SUCCESS("Staff created: staff1 / staff123"))

        self.stdout.write(self.style.SUCCESS("Done!"))
