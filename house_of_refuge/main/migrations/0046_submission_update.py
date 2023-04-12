# Generated by Django 3.2.12 on 2023-01-21 20:21

import django
from django.db import migrations, models


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
        migrations.CreateModel(
            name='Voivodeship',
            fields=[
                ('name', models.CharField(max_length=255, primary_key=True, serialize=False, unique=True)),
                ('namePl', models.CharField(max_length=255)),
                ('nameEN', models.CharField(max_length=255)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.RenameField(
            model_name='submission',
            old_name="how_long",
            new_name='how_long_other',
        ),
        migrations.AlterField(
            model_name='submission',
            name='how_long_other',
            field=models.CharField(help_text='For how long?', max_length=255, null=True, verbose_name='Length of stay'),
        ),
        migrations.AlterField(
            model_name='submission',
            name='description',
            field=models.CharField(help_text='Description', max_length=2048, verbose_name='Description'),
        ),
        migrations.AddField(
            model_name='submission',
            name='how_long',
            field=models.CharField(choices=[('upToWeek', 'Up to week'), ('month', 'Month'), ('twoMonthsOrMore', 'Two months or more')], help_text='For how long (in days)?', max_length=255, null=True, verbose_name='Length of stay'),
        ),
        migrations.AlterField(
            model_name='submission',
            name='people',
            field=models.CharField(max_length=2048, verbose_name='The number of people'),
        ),
        migrations.AddField(
            model_name='submission',
            name='voivodeships',
            field=models.ManyToManyField(to='main.Voivodeship', blank=True),
        ),
        migrations.CreateModel(
            name='Plans',
            fields=[
                ('name', models.CharField(max_length=255, primary_key=True, serialize=False, unique=True)),
                ('namePl', models.CharField(max_length=255)),
                ('nameEN', models.CharField(max_length=255)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='RefugeeGroup',
            fields=[
                ('name', models.CharField(max_length=255, primary_key=True, serialize=False, unique=True)),
                ('namePl', models.CharField(max_length=255)),
                ('nameEN', models.CharField(max_length=255)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='submission',
            name='groups_other',
            field=models.CharField(blank=True, help_text='Other groups', max_length=255, null=True, verbose_name='Other groups'),
        ),
        migrations.AddField(
            model_name='submission',
            name='plans_other',
            field=models.CharField(blank=True, help_text='Other plans', max_length=255, null=True, verbose_name='Other plans'),
        ),
        migrations.AddField(
            model_name='submission',
            name='groups',
            field=models.ManyToManyField(to='main.RefugeeGroup', blank=True),
        ),
        migrations.AddField(
            model_name='submission',
            name='plans',
            field=models.ManyToManyField(to='main.Plans', blank=True),
        ),
        migrations.CreateModel(
            name='AdditionalNeed',
            fields=[
                ('name', models.CharField(max_length=255, primary_key=True, serialize=False, unique=True)),
                ('namePl', models.CharField(max_length=255)),
                ('nameEN', models.CharField(max_length=255)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='submission',
            name='additional_needs_other',
            field=models.CharField(help_text='Other additional needs', max_length=1024, null=True, verbose_name='Other additional needs'),
        ),
        migrations.AddField(
            model_name='submission',
            name='additional_needs',
            field=models.ManyToManyField(to='main.AdditionalNeed', blank=True),
        ),
        migrations.CreateModel(
            name='Animal',
            fields=[
                ('name', models.CharField(max_length=255, primary_key=True, serialize=False, unique=True)),
                ('namePl', models.CharField(max_length=255)),
                ('nameEN', models.CharField(max_length=255)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='submission',
            name='allergies_other',
            field=models.CharField(blank=True, help_text='Other allergies', max_length=512, null=True, verbose_name='Other allergies'),
        ),
        migrations.AddField(
            model_name='submission',
            name='allergies',
            field=models.ManyToManyField(to='main.Animal', blank=True),
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('name', models.CharField(max_length=255, primary_key=True, serialize=False, unique=True)),
                ('namePl', models.CharField(max_length=255)),
                ('nameEN', models.CharField(max_length=255)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.RenameField(
            model_name='submission',
            old_name='languages',
            new_name='languages_other',
        ),
        migrations.AddField(
            model_name='submission',
            name='languages',
            field=models.ManyToManyField(to='main.Language', blank=True),
        ),
        migrations.AddField(
            model_name='submission',
            name='first_submission',
            field=models.BooleanField(null=True, verbose_name='First submission'),
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sex', models.CharField(choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], max_length=32, verbose_name='Sex')),
                ('age_range', models.CharField(choices=[('0-5', '0-5'), ('6-9', '6-9'), ('10-14', '10-14'), ('15-17', '15-17'), ('18-24', '18-24'), ('25-34', '25-34'), ('35-49', '35-49'), ('50+', '50+')], max_length=32, verbose_name='Age range')),
                ('submission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.submission')),
            ],
            options={
                'ordering': ['age_range'],
            },
        ),
        migrations.AlterField(
            model_name='submission',
            name='description',
            field=models.CharField(help_text='Description', max_length=2048, null=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='submission',
            name='how_long',
            field=models.CharField(choices=[('upToWeek', 'Up to week'), ('month', 'Month'), ('twoMonthsOrMore', 'Two months or more'), ('halfYear', 'Half a year'), ('asLongAsNeeded', 'As long as needed')], help_text='For how long (in days)?', max_length=255, null=True, verbose_name='Length of stay'),
        ),
        migrations.AddField(
            model_name='submission',
            name='current_place',
            field=models.CharField(choices=[('inPoland', 'In Poland'), ('onBorder', 'On border')], max_length=255, null=True, verbose_name='Current location'),
        ),
    ]
