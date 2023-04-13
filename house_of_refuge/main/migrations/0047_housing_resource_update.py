# Generated by Django 3.2.12 on 2023-02-06 22:57

from django.db import migrations, models

import house_of_refuge.main.models


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0046_submission_update'),
    ]

    operations = [
        migrations.AlterField(
            model_name='housingresource',
            name='resource',
            field=models.CharField(
                choices=[('home', 'House'), ('flat', 'Apartment'), ('room', 'Room'), ('couch', 'Couch'),
                         ('mattress', 'Mattress'), ('two_rooms', 'Two rooms'),
                         ('room_in_own_house', 'Room in own house'),
                         ('separate_part_of_apartment', 'Separate part of an apartment'),
                         ('bed_in_shared_room', 'Bed in shared room'),
                         ('place_in_hotel', 'Place in hotel, hostel or guesthouse')], null=True, max_length=1024,
                verbose_name='Resource'),
        ),
        migrations.AddField(
            model_name='housingresource',
            name='resource_other',
            field=models.CharField(max_length=1024, null=True, verbose_name='Resource other'),
        ),
        migrations.AddField(
            model_name='housingresource',
            name='adults_max_count',
            field=models.IntegerField(null=True, verbose_name='Adults to accommodate'),
        ),
        migrations.AddField(
            model_name='housingresource',
            name='animals_other',
            field=models.CharField(blank=True, help_text='Other animals', max_length=512, null=True,
                                   verbose_name='Other animals'),
        ),
        migrations.AddField(
            model_name='housingresource',
            name='children_max_count',
            field=models.IntegerField(null=True, verbose_name='Children to accommodate'),
        ),
        migrations.AddField(
            model_name='housingresource',
            name='facilities_other',
            field=models.CharField(help_text='Other facilities', max_length=1024, null=True,
                                   verbose_name='Other facilities'),
        ),
        migrations.RenameField(
            model_name='housingresource',
            old_name='languages',
            new_name='languages_other',
        ),
        migrations.AlterField(
            model_name='housingresource',
            name='languages_other',
            field=models.CharField(blank=True, help_text='Languages that the person speaks', max_length=1024, null=True,
                                   verbose_name='Languages'),
        ),
        migrations.AddField(
            model_name='housingresource',
            name='how_long',
            field=models.CharField(
                choices=[('upToWeek', 'Up to week'), ('month', 'Month'), ('twoMonthsOrMore', 'Two months or more'),
                         ('halfYear', 'Half a year'), ('asLongAsNeeded', 'As long as needed')],
                help_text='For how long (in days)?', max_length=255, null=True, verbose_name='Length of stay'),
        ),
        migrations.AddField(
            model_name='housingresource',
            name='animals',
            field=models.JSONField(default=house_of_refuge.main.models.empty_list_factory),
        ),
        migrations.AddField(
            model_name='housingresource',
            name='facilities',
            field=models.JSONField(default=house_of_refuge.main.models.empty_list_factory),
        ),
        migrations.AddField(
            model_name='housingresource',
            name='groups',
            field=models.JSONField(default=house_of_refuge.main.models.empty_list_factory),
        ),
        migrations.AddField(
            model_name='housingresource',
            name='languages',
            field=models.JSONField(default=house_of_refuge.main.models.empty_list_factory),
        ),
        migrations.AddField(
            model_name='housingresource',
            name='voivodeship',
            field=models.CharField(
                choices=[('all', 'all'), ('dolnoslaskie', 'dolnośląskie'), ('kujawskoPomorskie', 'kujawsko-pomorskie'),
                         ('lubelskie', 'lubelskie'), ('lubuskie', 'lubuskie'), ('lodzkie', 'łódzkie'),
                         ('malopolskie', 'małopolskie'), ('mazowieckie', 'mazowieckie'), ('opolskie', 'opolskie'),
                         ('podkarpackie', 'podkarpackie'), ('podlaskie', 'podlaskie'), ('pomorskie', 'pomorskie'),
                         ('slaskie', 'śląskie'), ('swietokrzyskie', 'świętokrzyskie'),
                         ('warminskoMazurskie', 'warmińsko-mazurskie'), ('wielkopolskie', 'wielkopolskie'),
                         ('zachodniopomorskie', 'zachodniopomorskie')], max_length=128, null=True),
        ),
    ]
