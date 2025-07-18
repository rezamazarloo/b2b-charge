# Generated by Django 5.2 on 2025-07-15 20:15

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('finance', '0001_initial'),
        ('inventory', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='creditrequest',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_credit_requests', to=settings.AUTH_USER_MODEL, verbose_name='user'),
        ),
        migrations.AddField(
            model_name='transactionhistory',
            name='credit_request',
            field=models.OneToOneField(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='credit_request_transaction_history', to='finance.creditrequest', verbose_name='credit request'),
        ),
        migrations.AddField(
            model_name='transactionhistory',
            name='seller',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='seller_transactions_history', to=settings.AUTH_USER_MODEL, verbose_name='seller user'),
        ),
        migrations.AddField(
            model_name='transactionhistory',
            name='simcard',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='simcard_transactions_history', to='inventory.simcard', verbose_name='simcard number'),
        ),
        migrations.AddIndex(
            model_name='creditrequest',
            index=models.Index(fields=['-created_at'], name='finance_cre_created_759d17_idx'),
        ),
        migrations.AddIndex(
            model_name='transactionhistory',
            index=models.Index(fields=['type'], name='finance_tra_type_60faa9_idx'),
        ),
        migrations.AddIndex(
            model_name='transactionhistory',
            index=models.Index(fields=['-created_at'], name='finance_tra_created_724b23_idx'),
        ),
    ]
