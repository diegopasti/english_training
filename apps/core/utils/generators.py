import logging

from faker import Faker
from django.contrib.auth.models import User
from django.db import IntegrityError

logger = logging.getLogger(__name__)
faker = Faker(locale='pt-BR')


def create_faker_valid_name():
    """ Generate a valid person name """
    name = faker.name().upper().replace("DRA. ", "").replace("DR. ", "")
    name = name.replace("SRA. ", "").replace("SRTA. ", "")
    name = name.replace("SR. ", "").replace("SR. ", "")
    return name


def create_user(superuser=False):

    name = create_faker_valid_name().split(" ")
    first_name = name[0]
    last_name = " ".join(name[1:]),
    email = f"{name[0]}.{name[-1]}@GMAIL.COM",
    username = ".".join(name),

    if superuser:
        create = User.objects.create_superuser
    else:
        create = User.objects.create_user

    try:
        user = create(username, email=email, password="user123")
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        logger.info("Successfully created user '%s'" % user.email.lower())
        return user

    except IntegrityError:
        logger.warning("User with email '%s' has already been created" % email.lower())


class BaseGenerator:

    model = None

    def __init__(self):
        self.admin = User.objects.filter(is_superuser=True).first()
        if not self.admin:
            self.admin = create_user(superuser=True)

    def save_object(self, data):
        data["created_by_id"] = self.admin.pk
        data["updated_by_id"] = self.admin.pk

        try:
            object = self.model(**data)
            object.save()
            return object

        except IntegrityError as exception:
            logger.info(str(exception))

    def generate(self):
        """ Abastract method to generate new objects """
        pass


class UserGenerator(BaseGenerator):

    model = User

    def save_object(self, data):
        try:
            user = self.model(**data)
            user.save()
            return user

        except IntegrityError as exception:
            print(str(exception))
            logger.info(str(exception))

    def get_generic_data(self) -> dict:
        """ Generate randon data to new User """

        name = create_faker_valid_name().split(" ")

        return {
            "first_name": name[0],
            "last_name": " ".join(name[1:]),
            "email": f"{name[0]}.{name[-1]}@GMAIL.COM",
            "username": ".".join(name),
            "password": "user123",
        }

    def generate(self) -> User:
        """ Generate new random Manager """
        return self.save_object(self.get_generic_data())
