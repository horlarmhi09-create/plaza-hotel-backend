import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "plaza_hotel.settings")
django.setup()

from accounts.models import User

if not User.objects.filter(username="admin").exists():
    User.objects.create_superuser(
        username="admin",
        email="horlarmhi09@gmail.com",
        password="giwa,.00jamiu"
    )
    print("Superuser created successfully!")
else:
    print("Superuser already exists.")
