# Generated by Django 4.2.5 on 2023-10-03 12:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('storre', '0010_alter_customer_options_remove_customer_email_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'permissions': [('cancel_order', 'can cancel order')]},
        ),
    ]