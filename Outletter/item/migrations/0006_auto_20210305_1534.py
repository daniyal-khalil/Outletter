# Generated by Django 3.1.4 on 2021-03-05 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('item', '0005_auto_20210210_1724'),
    ]

    operations = [
        migrations.AlterField(
            model_name='queryitem',
            name='shop',
            field=models.CharField(choices=[('www.koton.com', 'Koton'), ('www.lcwaikiki.com', 'Lcwaikiki'), ('www.boyner.com.tr', 'Boyner'), ('www.defacto.com.tr', 'Defacto'), ('www.trendyol.com', 'Trendyol'), ('www2.hm.com/tr_tr', 'Hm')], default='www.trendyol.com', max_length=256),
        ),
        migrations.AlterField(
            model_name='scrapeditem',
            name='shop',
            field=models.CharField(choices=[('www.koton.com', 'Koton'), ('www.lcwaikiki.com', 'Lcwaikiki'), ('www.boyner.com.tr', 'Boyner'), ('www.defacto.com.tr', 'Defacto'), ('www.trendyol.com', 'Trendyol'), ('www2.hm.com/tr_tr', 'Hm')], default='www.trendyol.com', max_length=256),
        ),
    ]