# Generated by Django 3.1.4 on 2021-01-25 17:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('item', '0002_auto_20210125_1441'),
    ]

    operations = [
        migrations.CreateModel(
            name='QueryItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('picture', models.ImageField(upload_to='item_pictures')),
                ('for_gender', models.CharField(choices=[('male', 'Male'), ('female', 'Female')], default='male', max_length=6)),
                ('shop', models.CharField(choices=[('www.koton.com', 'Koton'), ('www.lcwaikiki.com', 'Lcwaikiki'), ('www.boyner.com.tr', 'Boyner'), ('www.defacto.com.tr', 'Defacto'), ('www.trendyol.com', 'Trendyol'), ('www2.hm.com/tr_tr', 'Hm')], default='www.koton.com', max_length=256)),
                ('debug', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Query Item',
            },
        ),
        migrations.CreateModel(
            name='ScrapedItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('picture', models.ImageField(upload_to='item_pictures')),
                ('for_gender', models.CharField(choices=[('male', 'Male'), ('female', 'Female')], default='male', max_length=6)),
                ('shop', models.CharField(choices=[('www.koton.com', 'Koton'), ('www.lcwaikiki.com', 'Lcwaikiki'), ('www.boyner.com.tr', 'Boyner'), ('www.defacto.com.tr', 'Defacto'), ('www.trendyol.com', 'Trendyol'), ('www2.hm.com/tr_tr', 'Hm')], default='www.koton.com', max_length=256)),
                ('name', models.CharField(blank=True, max_length=128)),
                ('price', models.DecimalField(decimal_places=2, max_digits=7)),
                ('url', models.CharField(max_length=256)),
            ],
            options={
                'verbose_name': 'Scraped Item',
            },
        ),
        migrations.DeleteModel(
            name='Item',
        ),
    ]
