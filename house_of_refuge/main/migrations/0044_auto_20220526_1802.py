from django.db import migrations, models
import markdownx.models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0043_merge_20220425_2215'),
    ]

    operations = [
        migrations.AlterField(
            model_name='housingresource',
            name='status',
            field=models.CharField(choices=[('new', 'Fresh'), ('taken', 'Taken'), ('calling', 'Calling'), ('ignore', 'Ignore'), ('should_delete', 'For deletion'), ('contact_attempt', 'Próba kontaktu')], default='new', max_length=32, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='menupage',
            name='content_primary_language',
            field=markdownx.models.MarkdownxField(help_text="You can use <a href='https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax' target='_blank'>Markdown</a> here.", verbose_name='Content in the primary language'),
        ),
        migrations.AlterField(
            model_name='menupage',
            name='content_secondary_language',
            field=markdownx.models.MarkdownxField(blank=True, default='', help_text="You can use <a href='https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax' target='_blank'>Markdown</a> here.", verbose_name='Content in the secondary language'),
        ),
        migrations.AlterField(
            model_name='submission',
            name='status',
            field=models.CharField(choices=[('new', 'Fresh'), ('searching', 'Searching'), ('in_progress', 'Host found'), ('gone', 'Gone'), ('success', 'Success'), ('cancelled', 'Cancelled'), ('contact_attempt', 'Próba kontaktu')], default='new', max_length=32, verbose_name='Status'),
        ),
    ]
