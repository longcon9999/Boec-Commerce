# Generated by Django 3.2.3 on 2021-06-16 16:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0004_auto_20210616_1541'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ProductPromotion',
            new_name='Promotion',
        ),
    ]
