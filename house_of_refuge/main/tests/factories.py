import datetime

import factory.fuzzy
from factory import Faker
from factory.django import DjangoModelFactory

from house_of_refuge.main.models import HousingResource, HousingType, Submission, SubSource, Member


class HousingResourceFactory(DjangoModelFactory):
    name = Faker("name")
    email = Faker("email")
    zip_code = Faker("postcode")
    costs = "0"
    people_to_accommodate = Faker('pyint', min_value=1, max_value=6)
    accommodation_length = Faker('pyint', min_value=1, max_value=30)
    phone_number = Faker("phone_number")
    backup_phone_number = Faker("phone_number")
    transport = "warsaw"
    details = Faker("sentence")
    about_info = Faker("sentence")
    resource = factory.fuzzy.FuzzyChoice(HousingType.values)
    city_and_zip_code = Faker("city")
    address = Faker("street_address")
    age = Faker('pyint', min_value=23, max_value=65)
    when_to_call = "9 - 22"
    living_with_pets = "Nie"
    can_take_person_with_pets = "Tak"

    class Meta:
        model = HousingResource

    @factory.post_generation
    def languages(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            for lang in extracted:
                self.languages.add(lang)


class SubmissionFactory(DjangoModelFactory):
    name = Faker("name")
    email = Faker("email")
    phone_number = Faker("phone_number")
    people = Faker('pyint', min_value=1, max_value=20)
    how_long = "upToWeek"
    how_long_other = "3 dni (legacy)"
    description = Faker("sentence")
    traveling_with_pets = "Nie"
    can_stay_with_pets = "Nie"
    contact_person = Faker("name")
    source = SubSource.TERRAIN
    when = datetime.date(2023, 1, 1)
    languages_other = "someOtherLang"

    @factory.post_generation
    def languages(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for lang in extracted:
                self.languages.add(lang)

    @factory.post_generation
    def members(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for member in extracted:
                Member.objects.create(sex=member['sex'], age_range=member['ageRange'], submission=self)


    class Meta:
        model = Submission


# with factory.Faker.override_default_locale('pl_PL'):
#     ExampleFactory()


# @factory.Faker.override_default_locale('pl_PL')
# def test_foo(self):
#     user = ExampleFactory()
