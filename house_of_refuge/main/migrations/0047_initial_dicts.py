# Generated by Django 3.2.12 on 2023-01-31 15:21

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0046_submission_update'),
    ]

    operations = [
        migrations.RunSQL("""INSERT INTO main_additionalneed ("name", "namePl", "nameEN") VALUES
            ('firstFlorOrElevator', 'Parter lub budynek z windą', 'Ground floor or building with an elevator'),
            ('accessibleForWheelchairs', 'Miejsce dostępne dla osób poruszających się na wózku', 'A place accessible to people in a wheelchair'),
            ('childBed', 'Łóżeczko dla dziecka', 'A bed for a child'),
            ('petsAllowed', 'Możliwość zakwaterowania osoby/osób ze zwierzęciem/tami', 'Possibility of accommodating a person/people with a pet')
        """),
        migrations.RunSQL("""INSERT INTO main_animal ("name", "namePl", "nameEN") VALUES
            ('cats', 'Koty', 'Cats'),
            ('dogs', 'Psy', 'Dogs'),
            ('rodents', 'Gryzonie', 'Rodents')
        """),
        migrations.RunSQL("""INSERT INTO main_language ("name", "namePl", "nameEN") VALUES
            ('polish', 'Polski', 'Polish'),
            ('english', 'Angielski', 'English'),
            ('ukrainian', 'Ukraiński', 'Ukrainian'),
            ('russian', 'Rosyjski', 'Russian'),
            ('belarusian', 'Białoruski', 'Belarusian')
        """),
        migrations.RunSQL("""INSERT INTO main_refugeegroup ("name", "namePl", "nameEN") VALUES
            ('elderlyPersonIndependent', 'Osoba starsza (samodzielna)', 'Elderly person (independent)'),
            ('elderlyPersonWithGuardian', 'Osoba starsza (niesamodzielna - z opiekunem/ką)', 'An elderly person (not independent - with a guardian)'),
            ('man', 'Mężczyzna', 'Man'),
            ('personWithDisabilityIndependent', 'Osoba z niepełnosprawnością (samodzielna)', 'A person with a disability (independent)'),
            ('personWithDisabilityWithGuardian', 'Osoba z niepełnosprawnością (niesamodzielna - z opiekunem/ką)', 'A person with a disability (independent - with a guardian)'),
            ('refugeeCitizenshipNotUkrainian', 'Uchodźca/czyni z Ukrainy o innym obywatelstwie niż ukraińskie', 'A refugee from Ukraine with citizenship other than Ukrainian'),
            ('refugeeNationalityNotUkrainian', 'Uchodźca/czyni z Ukrainy o innej narodowości niż ukraińska', 'A refugee from Ukraine, with a nationality other than Ukrainian'),
            ('LGBTKAPlus', 'Osoba uchodźcza reprezentująca mniejszość płciową lub seksualną (LGBTQA+)', 'A person representing a gender or sexual minority (LGBTKA+)')
        """),
        migrations.RunSQL("""INSERT INTO main_plans ("name", "namePl", "nameEN") VALUES
            ('moveAbroad', 'przenieść się za granicę', 'move abroad'),
            ('rentApartmentOrRoomInPoland', 'wynająć mieszkanie/pokój w polsce', 'rent an apartment/room in Poland'),
            ('findJobAndRentApartmentOrRoomInPoland', 'znaleźć pracę i wynająć mieszkanie/pokój w Polsce', 'find a job and rent an apartment/room in Poland'),
            ('dontKnowYet', 'jeszcze nie wiemy', 'we don''t know yet')
        """),
        migrations.RunSQL("""INSERT INTO main_voivodeship ("name", "namePl", "nameEN") VALUES
            ('all', 'wszystkie', 'all'),
            ('dolnoslaskie', 'dolnośląskie', 'dolnośląskie'),
            ('kujawskoPomorskie', 'kujawsko-pomorskie', 'kujawsko-pomorskie'),
            ('lubelskie', 'lubelskie', 'lubelskie'),
            ('lubuskie', 'lubuskie', 'lubuskie'),
            ('lodzkie', 'łódzkie', 'łódzkie'),
            ('malopolskie', 'małopolskie', 'małopolskie'),
            ('mazowieckie', 'mazowieckie', 'mazowieckie'),
            ('opolskie', 'opolskie', 'opolskie'),
            ('podkarpackie', 'podkarpackie', 'podkarpackie'),
            ('podlaskie', 'podlaskie', 'podlaskie'),
            ('pomorskie', 'pomorskie', 'pomorskie'),
            ('slaskie', 'śląskie', 'śląskie'),
            ('swietokrzyskie', 'świętokrzyskie', 'świętokrzyskie'),
            ('warminskoMazurskie', 'warmińsko-mazurskie', 'warmińsko-mazurskie'),
            ('wielkopolskie', 'wielkopolskie', 'wielkopolskie'),
            ('zachodniopomorskie', 'zachodniopomorskie', 'zachodniopomorskie')
        """),
    ]
