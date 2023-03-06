import factory
from django.core.management.base import BaseCommand, CommandError
from tqdm import tqdm

from house_of_refuge.main.tests.factories import HousingResourceFactory, SubmissionFactory


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def add_arguments(self, parser):
        parser.add_argument('--hosts', default=100, type=int)
        parser.add_argument('--submissions', default=20, type=int)
        parser.add_argument('--locale', default="pl_PL", type=str)

    def handle(self, *args, **options):
        members = [
            {"ageRange": "0-5", "sex": "male"},
            {"ageRange": "18-24", "sex": "female"}
        ]
        locale = options['locale']
        host_count = options['hosts']
        subs_count = options['submissions']
        with factory.Faker.override_default_locale(locale):
            self.stdout.write(self.style.NOTICE(f'Generating {host_count} hosts...'))
            for _ in tqdm(range(options['hosts'])):
                HousingResourceFactory(languages=["polish", "ukrainian"], voivodeship="mazowieckie",
                                       facilities=['accessibleForWheelchairs'], animals=["rodents"],
                                       groups=["elderlyPersonWithGuardian"])
            self.stdout.write(self.style.NOTICE(f'Generating {subs_count} submissions...'))
            for _ in tqdm(range(options['submissions'])):
                SubmissionFactory(languages=["polish", "ukrainian"],
                                  voivodeships=["mazowieckie"],
                                  members=members,
                                  additional_needs=['accessibleForWheelchairs', 'firstFlorOrElevator'],
                                  allergies=["rodents"],
                                  plans=["rentApartmentOrRoomInPoland"],
                                  groups=["elderlyPersonWithGuardian"])
            self.stdout.write(self.style.SUCCESS('DONE.'))
