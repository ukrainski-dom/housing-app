import datetime

import pytest

from house_of_refuge.main.models import SubStatus, Coordinator, HousingResource, Submission, ObjectChange
from house_of_refuge.main.tests.factories import SubmissionFactory, HousingResourceFactory
from house_of_refuge.users.tests.factories import UserFactory


@pytest.mark.django_db
def test_matcher_changing(client):
    user1 = UserFactory()
    user2 = UserFactory()
    sub = SubmissionFactory()
    sub.matcher = user1
    sub.status = SubStatus.SEARCHING
    sub.save()

    # now user 2 wants to clear the matcher
    client.force_login(user2)
    response = client.post(f"/api/sub/update/{sub.id}", data={"fields": {"matcher_id": None, "status": "new"}},
                           content_type="application/json")
    assert response.status_code == 400
    sub.refresh_from_db()
    assert sub.matcher == user1
    assert sub.status == SubStatus.SEARCHING

    # now user2 is a coordinator -- the change is possible
    Coordinator.objects.create(user=user2, group="remote")
    response = client.post(f"/api/sub/update/{sub.id}", data={"fields": {"matcher_id": None, "status": "new"}},
                           content_type="application/json")
    assert response.status_code == 200
    sub.refresh_from_db()
    assert sub.matcher is None
    assert sub.status == SubStatus.NEW


@pytest.mark.django_db
def test_db_queries_on_sub_getting(client, user, django_assert_num_queries):
    client.force_login(user)
    user2 = UserFactory()
    for _ in range(40):
        SubmissionFactory()
        HousingResourceFactory()

    r = HousingResource.objects.first()
    r.owner = user2
    r.save()

    dropped = HousingResource.objects.last()
    dropped.is_dropped = True
    dropped.save()

    sub = Submission.objects.first()

    sub.receiver = user2
    sub.matcher = user
    sub.resource = r
    sub.save()
    ObjectChange.objects.create(host=r, submission=sub, user=user2, change="test")

    with django_assert_num_queries(4):
        response = client.get("/api/zgloszenia")
        assert len(response.json()['data']['submissions']) == 40
        assert response.status_code == 200

    for _ in range(40):
        SubmissionFactory()
        HousingResourceFactory()

    with django_assert_num_queries(4):
        response = client.get("/api/zgloszenia")
        assert len(response.json()['data']['submissions']) == 80
        assert response.status_code == 200


@pytest.mark.django_db
def test_db_queries_on_resource_getting(client, user, django_assert_num_queries):
    client.force_login(user)
    user2 = UserFactory()
    for _ in range(40):
        SubmissionFactory()
        HousingResourceFactory()

    r = HousingResource.objects.first()
    r.owner = user2
    r.save()

    dropped = HousingResource.objects.last()
    dropped.is_dropped = True
    dropped.save()

    sub = Submission.objects.first()

    sub.receiver = user2
    sub.matcher = user
    sub.save()

    with django_assert_num_queries(3):
        response = client.get("/api/zasoby")
        assert response.status_code == 200


@pytest.mark.django_db
def test_housing_resource_endpoint(client):
    data = dict(
        name="Jan III Sobieski",
        about_info="I have a a fairly big place to share",
        resource="flat",
        city_and_zip_code="Warsaw, 02-958",
        zip_code="02-958",
        address="Stanisława Kostki Potockiego 10/16",
        people_to_accommodate="300",
        age="393",
        languages="polish, german, turkish",
        when_to_call="9-22",
        costs="0",
        availability="2022-03-01",
        accommodation_length="365",
        details="I just wanna help",
        transport="poland",
        phone_number="600 500 500",
        backup_phone_number="601 500 500",
        email="fidei-defensor@onet.pl",
        extra="",
    )

    response = client.post("/api/stworz_zasob", data=data, content_type="application/json")
    assert response.status_code == 201, response.json()

    resource = HousingResource.objects.get()
    data["about_info"] = "I added something new"

    # no token passed
    response = client.put("/api/stworz_zasob", data=data, content_type="application/json")
    assert response.status_code == 400, response.json()

    # now we're passing dubious token
    data['token'] = '123'
    response = client.put("/api/stworz_zasob", data=data, content_type="application/json")
    assert response.status_code == 404, response.json()

    # now we're passing proper token
    data['token'] = resource.token
    response = client.put("/api/stworz_zasob", data=data, content_type="application/json")
    assert response.status_code == 202, response.json()

    resource.refresh_from_db()
    assert resource.about_info == "I added something new"

    response = client.delete("/api/stworz_zasob", data={"token": resource.token}, content_type="application/json")
    assert response.status_code == 204
    assert HousingResource.objects.count() == 0


@pytest.mark.django_db
def test_create_submission_integration_v2_endpoint(client):
    data = dict(
        name="Jan Kowalski",
        currentPlace="inPoland",
        phoneNumber="+48123123123",
        email="test@example.com",
        voivodeships=["mazowieckie"],
        adults=[
            {
                "sex": "male",
                "ageRange": "18-24"
            }
        ],
        children=[
            {
                "sex": "female",
                "ageRange": "0-5"
            }
        ],
        fromDate="2023-01-01",
        needPeriod="upToWeek",
        additionalNeeds=["firstFlorOrElevator", "accessibleForWheelchairs"],
        additionalNeedsOther="someOtherNeed",
        allergies=["cats", "dogs"],
        allergiesOther="someOtherAllergy",
        languages=[
            "polish",
            "english"
        ],
        languagesOther="someOtherLang",
        groups=["elderlyPersonWithGuardian", "refugeeCitizenshipNotUkrainian"],
        groupsOther="someOtherGroup",
        plans=["findJobAndRentApartmentOrRoomInPoland"],
        plansOther="someOtherPlans",
        additionalInfo="someAdditionalInfo",
        firstSubmission=True,
        newsletterAgreement=True
    )

    response = client.post("/api/submission", data=data, content_type="application/json")
    assert response.status_code == 201

    response_json = response.json()
    sub_id = response_json["id"]
    assert type(sub_id) == int

    sub_from_db = Submission.objects.get(id=sub_id)

    assert sub_from_db.name == "Jan Kowalski"
    assert sub_from_db.current_place == "inPoland"
    assert sub_from_db.phone_number == "+48123123123"
    assert sub_from_db.email == "test@example.com"
    assert sub_from_db.when == datetime.date(2023, 1, 1)
    assert sub_from_db.how_long == "upToWeek"
    assert sub_from_db.additional_needs_other == "someOtherNeed"
    assert sub_from_db.allergies_other == "someOtherAllergy"
    assert sub_from_db.languages_other == "someOtherLang"
    assert sub_from_db.groups_other == "someOtherGroup"
    assert sub_from_db.plans_other == "someOtherPlans"
    assert sub_from_db.description == "someAdditionalInfo"
    assert sub_from_db.first_submission

    assert {*sub_from_db.voivodeships} == {"mazowieckie"}
    assert {*sub_from_db.additional_needs} == {"firstFlorOrElevator", "accessibleForWheelchairs"}
    assert {*sub_from_db.allergies} == {"cats", "dogs"}
    assert {*sub_from_db.languages} == {"polish", "english"}
    assert {*sub_from_db.groups} == {"elderlyPersonWithGuardian", "refugeeCitizenshipNotUkrainian"}
    assert {*sub_from_db.plans} == {"findJobAndRentApartmentOrRoomInPoland"}

    assert len(sub_from_db.members) == 2
    members = sorted(sub_from_db.members, key=lambda m: m['ageRange'])
    assert [member['sex'] for member in members] == ['female', 'male']
    assert [member['ageRange'] for member in members] == ['0-5', '18-24']


@pytest.mark.django_db
def test_create_submission_integration_v2_endpoint_minimal_data(client):
    data = dict(
        name="Jan Kowalski",
        currentPlace="inPoland",
        phoneNumber="+48123123123",
        email="test@example.com",
        voivodeships=[],
        adults=[],
        children=[],
        fromDate="2023-01-01",
        needPeriod="upToWeek",
        additionalNeeds=[],
        additionalNeedsOther=None,
        allergies=[],
        allergiesOther=None,
        languages=[],
        languagesOther=None,
        groups=[],
        groupsOther=None,
        plans=[],
        plansOther=None,
        additionalInfo='',
        firstSubmission=True,
        newsletterAgreement=True
    )

    response = client.post("/api/submission", data=data, content_type="application/json")
    assert response.status_code == 201

    response_json = response.json()
    sub_id = response_json["id"]
    assert type(sub_id) == int

    sub_from_db = Submission.objects.get(id=sub_id)

    assert sub_from_db.name == "Jan Kowalski"
    assert sub_from_db.current_place == "inPoland"
    assert sub_from_db.phone_number == "+48123123123"
    assert sub_from_db.email == "test@example.com"
    assert sub_from_db.when == datetime.date(2023, 1, 1)
    assert sub_from_db.how_long == "upToWeek"
    assert sub_from_db.additional_needs_other is None
    assert sub_from_db.allergies_other is None
    assert sub_from_db.languages_other is None
    assert sub_from_db.groups_other is None
    assert sub_from_db.plans_other is None
    assert sub_from_db.description == ''
    assert sub_from_db.first_submission
    assert sub_from_db.voivodeships == []
    assert sub_from_db.additional_needs == []
    assert sub_from_db.allergies == []
    assert sub_from_db.languages == []
    assert sub_from_db.groups == []
    assert sub_from_db.plans == []
    assert sub_from_db.members == []


@pytest.mark.django_db
def test_create_housing_resource_integration_v2_endpoint(client):
    data = dict(
        name="Jan Kowalski",
        phoneNumber="+48123123123",
        email="test@example.com",
        voivodeship="mazowieckie",
        zipCode="03-984",
        resourceType="separate_part_of_apartment",
        resourceTypeOther="otherResourceType",
        facilities=["firstFlorOrElevator", "accessibleForWheelchairs"],
        facilitiesOther="someOtherNeed",
        adultsMaxCount=2,
        childrenMaxCount=4,
        fromDate="2023-01-01",
        period="upToWeek",
        groups=["elderlyPersonWithGuardian", "refugeeCitizenshipNotUkrainian"],
        animals=["cats", "dogs"],
        animalsOther="someOtherAnimal",
        languages=[
            "polish",
            "english"
        ],
        languagesOther="someOtherLang",
        additionalInfo="someAdditionalInfo",
        newsletterAgreement=True,
    )

    response = client.post("/api/housing_resource", data=data, content_type="application/json")
    assert response.status_code == 201

    response_json = response.json()
    resource_id = response_json["id"]
    assert type(resource_id) == int

    resource_from_db = HousingResource.objects.get(id=resource_id)

    assert resource_from_db.name == "Jan Kowalski"
    assert resource_from_db.phone_number == "+48123123123"
    assert resource_from_db.email == "test@example.com"
    assert resource_from_db.voivodeship == "mazowieckie"
    assert resource_from_db.zip_code == "03-984"
    assert resource_from_db.resource == "separate_part_of_apartment"
    assert resource_from_db.resource_other == "otherResourceType"
    assert resource_from_db.facilities_other == "someOtherNeed"
    assert resource_from_db.adults_max_count == 2
    assert resource_from_db.children_max_count == 4
    assert resource_from_db.availability == datetime.date(2023, 1, 1)
    assert resource_from_db.how_long == "upToWeek"
    assert resource_from_db.animals_other == "someOtherAnimal"
    assert resource_from_db.languages_other == "someOtherLang"
    assert resource_from_db.details == "someAdditionalInfo"
    assert {*resource_from_db.facilities} == {"firstFlorOrElevator", "accessibleForWheelchairs"}
    assert {*resource_from_db.languages} == {"polish", "english"}
    assert {*resource_from_db.animals} == {"cats", "dogs"}
    assert {*resource_from_db.groups} == {"elderlyPersonWithGuardian", "refugeeCitizenshipNotUkrainian"}


@pytest.mark.django_db
def test_create_housing_resource_integration_v2_endpoint_minimal_data(client):
    data = dict(
        name="Jan Kowalski",
        phoneNumber="+48123123123",
        email="test@example.com",
        voivodeship="mazowieckie",
        zipCode="03-984",
        resourceType=None,
        resourceTypeOther=None,
        facilities=[],
        facilitiesOther=None,
        adultsMaxCount=2,
        childrenMaxCount=4,
        fromDate="2023-01-01",
        period="upToWeek",
        groups=[],
        animals=[],
        animalsOther=None,
        languages=[],
        languagesOther=None,
        additionalInfo='',
        newsletterAgreement=True,
    )

    response = client.post("/api/housing_resource", data=data, content_type="application/json")
    assert response.status_code == 201

    response_json = response.json()
    resource_id = response_json["id"]
    assert type(resource_id) == int

    resource_from_db = HousingResource.objects.get(id=resource_id)

    assert resource_from_db.name == "Jan Kowalski"
    assert resource_from_db.phone_number == "+48123123123"
    assert resource_from_db.email == "test@example.com"
    assert resource_from_db.voivodeship == "mazowieckie"
    assert resource_from_db.zip_code == "03-984"
    assert resource_from_db.resource is None
    assert resource_from_db.resource_other is None
    assert resource_from_db.facilities_other is None
    assert resource_from_db.adults_max_count == 2
    assert resource_from_db.children_max_count == 4
    assert resource_from_db.availability == datetime.date(2023, 1, 1)
    assert resource_from_db.how_long == "upToWeek"
    assert resource_from_db.animals_other is None
    assert resource_from_db.languages_other is None
    assert resource_from_db.details == ''
    assert resource_from_db.facilities == []
    assert resource_from_db.languages == []
    assert resource_from_db.animals == []
    assert resource_from_db.groups == []
