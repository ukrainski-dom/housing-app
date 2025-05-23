# Generated by Django 3.2.12 on 2022-06-05 20:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0044_auto_20220526_1802'),
    ]

    operations = [
        migrations.AlterField(
            model_name='housingresource',
            name='about_info',
            field=models.TextField(blank=True, help_text="how old are you? who do you live with (if you'll host at your place)?", max_length=2048, verbose_name='Something about you'),
        ),
        migrations.AlterField(
            model_name='housingresource',
            name='details',
            field=models.TextField(blank=True, help_text='A bunch of information about the place - presence of animals, languages spoken by tenants, availability of bed linen and towels, others', max_length=2048, verbose_name='Details'),
        ),
        migrations.AlterField(
            model_name='housingresource',
            name='status',
            field=models.CharField(choices=[('new', 'Fresh'), ('booked', 'Booked'), ('taken', 'Taken'), ('calling', 'Calling'), ('ignore', 'Ignore'), ('should_delete', 'For deletion'), ('contact_attempt', 'Próba kontaktu')], default='new', max_length=32, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='housingresource',
            name='transport',
            field=models.CharField(blank=True, choices=[('warsaw', 'Warsaw'), ('poland', 'Poland'), ('none', 'None')], max_length=16, verbose_name='Transport'),
        ),
    ]
