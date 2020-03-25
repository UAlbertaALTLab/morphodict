# Generated by Django 2.2.11 on 2020-03-25 02:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0009_wordform_ascii_text'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='wordform',
            index=models.Index(fields=['ascii_text'], name='API_wordfor_ascii_t_a0b723_idx'),
        ),
    ]
