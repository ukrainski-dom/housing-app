# Generated by Django 3.2.12 on 2023-01-21 20:21

import django
from django.db import migrations, models

import house_of_refuge.main.models


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0045_auto_20220605_2259'),
    ]

    operations = [
        migrations.AddField(
            model_name='submission',
            name='email',
            field=models.EmailField(max_length=254, null=True, verbose_name='Email'),
        ),
        migrations.RenameField(
            model_name='submission',
            old_name="how_long",
            new_name='how_long_other',
        ),
        migrations.AlterField(
            model_name='submission',
            name='description',
            field=models.CharField(help_text='Description', max_length=2048, verbose_name='Description'),
        ),
        migrations.AddField(
            model_name='submission',
            name='how_long',
            field=models.CharField(
                choices=[('upToWeek', 'Up to week'), ('month', 'Month'), ('twoMonthsOrMore', 'Two months or more')],
                help_text='For how long (in days)?', max_length=255, null=True, verbose_name='Length of stay'),
        ),
        migrations.AddField(
            model_name='submission',
            name='groups_other',
            field=models.CharField(blank=True, help_text='Other groups', max_length=255, null=True,
                                   verbose_name='Other groups'),
        ),
        migrations.AddField(
            model_name='submission',
            name='plans_other',
            field=models.CharField(blank=True, help_text='Other plans', max_length=255, null=True,
                                   verbose_name='Other plans'),
        ),
        migrations.AddField(
            model_name='submission',
            name='additional_needs_other',
            field=models.CharField(help_text='Other additional needs', max_length=1024, null=True,
                                   verbose_name='Other additional needs'),
        ),
        migrations.AddField(
            model_name='submission',
            name='allergies_other',
            field=models.CharField(blank=True, help_text='Other allergies', max_length=512, null=True,
                                   verbose_name='Other allergies'),
        ),
        migrations.RenameField(
            model_name='submission',
            old_name='languages',
            new_name='languages_other',
        ),
        migrations.AddField(
            model_name='submission',
            name='first_submission',
            field=models.BooleanField(null=True, verbose_name='First submission'),
        ),
        migrations.AlterField(
            model_name='submission',
            name='description',
            field=models.CharField(help_text='Description', max_length=2048, null=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='submission',
            name='how_long',
            field=models.CharField(
                choices=[('upToWeek', 'Up to week'), ('month', 'Month'), ('twoMonthsOrMore', 'Two months or more'),
                         ('halfYear', 'Half a year'), ('asLongAsNeeded', 'As long as needed')],
                help_text='For how long (in days)?', max_length=255, null=True, verbose_name='Length of stay'),
        ),
        migrations.AddField(
            model_name='submission',
            name='current_place',
            field=models.CharField(choices=[('inPoland', 'In Poland'), ('onBorder', 'On border')], max_length=255,
                                   null=True, verbose_name='Current location'),
        ),
        migrations.AddField(
            model_name='submission',
            name='additional_needs',
            field=models.JSONField(default=house_of_refuge.main.models.empty_list_factory),
        ),
        migrations.AddField(
            model_name='submission',
            name='allergies',
            field=models.JSONField(default=house_of_refuge.main.models.empty_list_factory),
        ),
        migrations.AddField(
            model_name='submission',
            name='groups',
            field=models.JSONField(default=house_of_refuge.main.models.empty_list_factory),
        ),
        migrations.AddField(
            model_name='submission',
            name='languages',
            field=models.JSONField(default=house_of_refuge.main.models.empty_list_factory),
        ),
        migrations.AddField(
            model_name='submission',
            name='members',
            field=models.JSONField(default=house_of_refuge.main.models.empty_list_factory),
        ),
        migrations.AddField(
            model_name='submission',
            name='plans',
            field=models.JSONField(default=house_of_refuge.main.models.empty_list_factory),
        ),
        migrations.AddField(
            model_name='submission',
            name='voivodeships',
            field=models.JSONField(default=house_of_refuge.main.models.empty_list_factory),
        ),
    ]
