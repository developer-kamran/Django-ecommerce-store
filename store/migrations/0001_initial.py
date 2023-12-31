# Generated by Django 4.2.5 on 2023-09-30 08:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_countries.fields
import store.utils


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BillingAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('receiver', models.CharField(max_length=30)),
                ('address', models.CharField(max_length=256)),
                ('phone_no', models.CharField(max_length=14)),
                ('zip', models.CharField(blank=True, max_length=10, null=True)),
                ('country', django_countries.fields.CountryField(max_length=2)),
                ('city', models.CharField(max_length=100)),
                ('instructions', models.TextField(blank=True, null=True)),
                ('save_info', models.BooleanField(blank=True, default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256)),
                ('slug', models.SlugField(blank=True, max_length=256, unique=True)),
                ('description', models.TextField()),
                ('image', models.ImageField(blank=True, null=True, upload_to=store.utils.upload_to)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('discount_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('category', models.CharField(choices=[('S', 'Shirt'), ('SW', 'Shirt Wear'), ('OW', 'Outwear')], max_length=2)),
                ('label', models.CharField(choices=[('P', 'primary'), ('S', 'secondary'), ('D', 'danger')], max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='RedeemCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=6, unique=True)),
                ('is_valid', models.BooleanField(default=True)),
                ('is_used', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stripe_charge_id', models.CharField(max_length=100)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('timestamp', models.DateField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=1)),
                ('ordered', models.BooleanField(default=False)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.item')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.CharField(max_length=5, null=True, unique=True)),
                ('start_date', models.DateTimeField(auto_now_add=True)),
                ('ordered_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('ordered', models.BooleanField(default=False)),
                ('has_redeemed', models.BooleanField(default=False)),
                ('delivered', models.BooleanField(blank=True, default=False)),
                ('billing_address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='store.billingaddress')),
                ('items', models.ManyToManyField(to='store.orderitem')),
                ('payment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='store.payment')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
