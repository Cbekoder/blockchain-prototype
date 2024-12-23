import uuid
from io import BytesIO

import qrcode
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.utils.crypto import get_random_string
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.views import View
from .models import User


class signupView(View):
    def get(self, request):
        return render(request, 'signup.html')

    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        errors = []
        if password != confirm_password:
            errors.append("Passwords do not match!")
            return render(request, 'signup.html', {'errors': errors})
        if User.objects.filter(username=username).exists():
            errors.append("Username already taken!")
            return render(request, 'signup.html', {'errors': errors})
        try:
            wallet_address = "0x" +uuid.uuid4().hex
            public_key = get_random_string(64)
            private_key = get_random_string(64)

            qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
            qr.add_data(wallet_address)
            qr.make(fit=True)

            img = qr.make_image(fill='black', back_color='white')

            qr_image = BytesIO()
            img.save(qr_image, format='PNG')
            qr_image.seek(0)

            qr_file = ContentFile(qr_image.read(), name=f'{wallet_address}_qr.png')

            user = User.objects.create_user(
                username=username,
                password=password,
                wallet_address=wallet_address,
                wallet_qr = qr_file,
                public_key=public_key,
                private_key=private_key,
                balance=100,
                stake_amount=0,
                is_validator=False,
            )
            user.save()

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('/')
            else:
                errors.append("Authentication failed!")
                return render(request, 'signup.html', {'errors': errors})

        except Exception as e:
            errors.append(f"An error occurred: {str(e)}")
            return render(request, 'signup.html', {'errors': errors})

class loginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            return render(request, 'login.html', {"errors": "Invalid username or password"})


def logoutView(request):
    logout(request)
    return redirect('login')


class user_profile(View):
    def get(self, request):
        if request.user.is_authenticated:
            user = User.objects.get(id=request.user.id)
            context = {
                'user': user,
                # 'balance': balance
            }
            return render(request, 'profile.html', context)
        return redirect('login')

def update_profile_picture(request):
    if request.user.is_authenticated and request.method == 'POST':
        if 'profile_picture' in request.FILES:
            profile_picture = request.FILES['profile_picture']
            user_profile = request.user
            user_profile.profile_picture = profile_picture
            user_profile.save()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False})
    return JsonResponse({'success': False})

