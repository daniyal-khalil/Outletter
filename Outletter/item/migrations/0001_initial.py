# Generated by Django 3.1.4 on 2020-12-18 16:08

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('price', models.DecimalField(decimal_places=2, max_digits=7)),
                ('url', models.CharField(max_length=256)),
                ('picture', models.CharField(max_length=256)),
            ],
            options={
                'verbose_name': 'Item',
            },
        ),
    ]