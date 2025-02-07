# Generated by Django 4.2.16 on 2024-12-26 17:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_menuitem_photo_url_alter_restaurant_photo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('received', 'Received'), ('active', 'Active'), ('picked_up', 'Picked Up'), ('delivered', 'Delivered'), ('inactive', 'Inactive')], default='pending', max_length=20),
        ),
    ]
