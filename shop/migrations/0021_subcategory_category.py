# Generated by Django 4.2.3 on 2023-10-21 06:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0020_alter_product_subcategory'),
    ]

    operations = [
        migrations.AddField(
            model_name='subcategory',
            name='category',
            field=models.ForeignKey(default=4, on_delete=django.db.models.deletion.CASCADE, to='shop.category'),
        ),
    ]
