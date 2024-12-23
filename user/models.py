from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    wallet_address = models.CharField(max_length=64, unique=True, null=True, blank=True)
    public_key = models.TextField(null=True, blank=True)
    private_key = models.TextField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    wallet_qr = models.ImageField(upload_to='wallet_qr/', null=True, blank=True)
    stake_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_validator = models.BooleanField(default=False)
    transaction_count = models.PositiveIntegerField(default=0)
    balance = models.FloatField(default=100)
    status = models.CharField(max_length=20, choices=[('active', 'Active'), ('blocked', 'Blocked'), ('inactive', 'Inactive')], default='active')
    join_date = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.username