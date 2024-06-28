import os

from django.core import management
from django.core.management.base import BaseCommand

from data.fixture_entities import create_entities, create_customers
from data.fixture_managers import create_managers
from data.fixture_users import create_users


class Command(BaseCommand):
    help = ("Cleans database and migration files, recreates and applies migrations and generates"
            " initial load with random data in the database.")

    def _clear_database(self):
        self.stdout.write(
            self.style.NOTICE("Recreating database")
        )

        management.call_command('flush')

    def _migrate_apps(self):
        self.stdout.write(
            self.style.NOTICE("\n\nRecreating migration files")
        )
        management.call_command('makemigrations')

        self.stdout.write(
            self.style.NOTICE("\n\nApplying migration files")
        )
        management.call_command('migrate')

    def _reset_migrations(self):
        self.stdout.write(
            self.style.NOTICE("\n\nRemoving migration files")
        )

        apps_directory = os.path.join(os.getcwd(), "apps")

        i = 0
        for subdir, dirs, files in os.walk(apps_directory):
            if os.path.basename(os.path.normpath(subdir)) == "migrations":
                for migration in files:
                    if migration != "__init__.py":
                        fullpath = os.path.join(apps_directory, subdir, migration)
                        os.remove(fullpath)
                        self.stdout.write(
                            self.style.SUCCESS("Successfully deleted migration %s" % fullpath)
                        )

    def handle(self, *args, **options):
        self._clear_database()
        self._reset_migrations()
        self._migrate_apps()
