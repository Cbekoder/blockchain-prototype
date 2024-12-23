from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('transaction/', TransactionView.as_view(), name='transaction'),
    path('blockchain/', blockchain_view, name='blockchain'),
    path('qr/', QRView.as_view(), name='qr'),
    path('validator/', ValidatorView.as_view(), name='validator'),
]