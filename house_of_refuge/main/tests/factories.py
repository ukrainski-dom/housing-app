import datetime

import factory.fuzzy
from factory import Faker
from factory.django import DjangoModelFactory

from house_of_refuge.main.models import HousingResource, HousingType, Submission, SubSource


class HousingResourceFactory(DjangoModelFactory):
    name = Faker("name")
    email = Faker("email")
    zip_code = Faker("postcode")
    costs = "0"
    people_to_accommodate = 0
    phone_number = Faker("phone_number")
    backup_phone_number = Faker("phone_number")
    transport = "warsaw"
    details = Faker("sentence")
    about_info = Faker("sentence")
    resource = factory.fuzzy.FuzzyChoice(HousingType.values)
    resource_other = "otherResourceType"
    city_and_zip_code = Faker("city")
    address = Faker("street_address")
    age = Faker('pyint', min_value=23, max_value=65)
    when_to_call = "9 - 22"
    living_with_pets = "Nie"
    can_take_person_with_pets = "Tak"
    languages_other = "someOtherLang"
    availability = datetime.date(2023, 1, 1)
    how_long = "upToWeek"
    children_max_count = 3
    adults_max_count = 2
    facilities_other = "otherFacilities"
    animals_other = "someOtherAnimal"
    languages = ["polish", "ukrainian"]
    voivodeship = "mazowieckie"
    facilities = ['accessibleForWheelchairs']
    animals = ["rodents"]
    groups = ["elderlyPersonWithGuardian"]

    class Meta:
        model = HousingResource


class SubmissionFactory(DjangoModelFactory):
    name = Faker("name")
    current_place = "inPoland"
    email = Faker("email")
    phone_number = Faker("phone_number")
    people = ''
    how_long = "upToWeek"
    how_long_other = "3 dni (legacy)"
    description = Faker("sentence")
    traveling_with_pets = "Nie"
    can_stay_with_pets = "Nie"
    contact_person = Faker("name")
    source = SubSource.TERRAIN
    when = datetime.date(2023, 1, 1)
    languages_other = "someOtherLang"
    additional_needs_other = "someOtherNeed"
    groups_other = "someOtherGroup"
    plans_other = "someOtherPlans"
    allergies_other = "someOtherAllergy"
    first_submission = True
    languages = ["polish", "ukrainian"]
    voivodeships = ["mazowieckie"]
    members = [
        {"ageRange": "0-5", "sex": "male"},
        {"ageRange": "18-24", "sex": "female"}
    ]
    additional_needs = ['accessibleForWheelchairs', 'firstFlorOrElevator']
    allergies = ["rodents"]
    plans = ["rentApartmentOrRoomInPoland"]
    groups = ["elderlyPersonWithGuardian"]

    class Meta:
        model = Submission

# with factory.Faker.override_default_locale('pl_PL'):
#     ExampleFactory()


# @factory.Faker.override_default_locale('pl_PL')
# def test_foo(self):
#     user = ExampleFactory()
