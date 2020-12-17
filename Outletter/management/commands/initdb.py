from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import BaseCommand

class Command(BaseCommand):
    def handle(self, *args, **options):
        if settings.DEBUG is False:
            self.stderr.write(
                self.style.ERROR("You must enable DEBUG mode to run this command.")
            )
            return
        
        user = User.objects.filter(username="toni").first()
        if not user:
            User.objects.create_superuser("toni", "toni@bilkent.com", "secret")
        # Write code for initialization here After we make our DB design that is.

