# Generated by Django 4.2.16 on 2024-11-25 16:00

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Conversation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('speaker', models.TextField()),
                ('content', models.TextField()),
                ('date', models.DateField(auto_now_add=True)),
                ('user', models.TextField()),
            ],
        ),
    ]
