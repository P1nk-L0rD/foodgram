# Generated by Django 3.2.3 on 2024-07-07 11:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_auto_20240707_1442'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='slug',
            field=models.SlugField(max_length=150, unique=True, verbose_name='Слаг'),
        ),
    ]
