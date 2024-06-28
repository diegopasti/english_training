import logging

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from apps.core.utils import BaseGenerator

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = ("Populate database with random objects for testing")

    def _generate(self, generator: BaseGenerator, quantity, message):
        """ Execute generators """
        logger.info(msg="\n\n{message}")
        print(message)

        for item in range(quantity):
            object = generator().generate()
            print(object,"Created")

    def _populate_database(self):
        logger.info(msg="Populating Database")

        generators = [
            #{"generator": UserGenerator, "quantity": 50, "message": "Core > Creating Users"},
        ]

        for item in generators:
            self._generate(**item)

        logger.info(msg="\n\nDatabase was successfully populated")

    def handle(self, *args, **options):

        admin = User.objects.filter(is_superuser=True).first()
        if not admin:
            logger.error(msg="Error! Create a superuser before starting populate the database")
            exit(1)

        self._populate_database()





