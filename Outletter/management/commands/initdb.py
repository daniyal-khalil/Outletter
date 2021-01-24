from django.conf import settings
from django.core.management import BaseCommand

from Outletter.user.models import User

class Command(BaseCommand):
    def handle(self, *args, **options):
        if settings.DEBUG is False:
            self.stderr.write(
                self.style.ERROR("You must enable DEBUG mode to run this command.")
            )
            return
        
        user = User.objects.filter(user_name="toni").first()
        if not user:
            User.objects.create_superuser(email="toni@bilkent.com", user_name="toni",
                                 first_name="tony", last_name="guy", password="secret")
        # Write code for initialization here After we make our DB design that is.

