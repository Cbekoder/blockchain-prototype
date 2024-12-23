import uuid
from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.db import transaction
from django.core.files.base import ContentFile
from django.views import View
import qrcode
from io import BytesIO


from .blockchain import blockchain
from user.models import User
from .models import Transaction, Block


def home(request):
    return render(request, 'index.html', {'values': [1, 2, 3, 4, 5, 6]})

class TransactionView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return render(request, 'transaction.html')
        return redirect('login')

    def post(self, request):
        if request.user.is_authenticated:
            recipient_wallet_address = request.POST.get('address')
            amount = float(request.POST.get('amount'))
            sender = request.user
            # data = request.POST.get('data', '')

            errors = []

            try:
                recipient = User.objects.get(wallet_address=recipient_wallet_address)

                latest_block = Block.objects.all().order_by('timestamp').last()

                if sender.balance < amount:
                    errors.append("Insufficient balance")
                    return render(request, 'transaction.html', {'errors': errors})

                if latest_block :
                    time_difference = timezone.now() - latest_block.timestamp

                    if time_difference <= timedelta(minutes=1):
                        new_block = latest_block
                    else:
                        new_block = Block.objects.create(
                            block_hash=str(uuid.uuid4().hex),
                            previous_block_hash=latest_block.block_hash,
                            timestamp=timezone.now(),
                            difficulty=5,
                            size=0,
                            transaction_count=0,
                            miner=None
                        )
                else:
                    new_block = Block.objects.create(
                        block_hash=str(uuid.uuid4().hex),
                        previous_block_hash=latest_block.block_hash,
                        timestamp=timezone.now(),
                        difficulty=5,
                        size=0,
                        transaction_count=0,
                        miner=None
                    )


                transaction = Transaction.objects.create(
                    block=new_block,
                    from_address=sender,
                    to_address=recipient,
                    value=amount,
                    data=None,
                    timestamp=timezone.now(),
                    status=True,
                    signature=None
                )

                new_block.transaction_count += 1
                new_block.save()

                sender.balance -= amount
                sender.transaction_count += 1
                recipient.balance += amount
                recipient.transaction_count += 1
                sender.save()
                recipient.save()

                return redirect('blockchain')

            except User.DoesNotExist:
                errors.append("Recipient does not exist!")
                return render(request, 'transaction.html', {'errors': errors})

            except Exception as e:
                errors.append(f"An error occurred: {str(e)}")
                return render(request, 'transaction.html', {'errors': errors})

        return redirect('login')

def blockchain_view(request):
    if request.user.is_authenticated:
        context = {
            'transactions': Transaction.objects.all().order_by('-timestamp')[:20],
        }
        return render(request, 'blockchain.html', context)
    return redirect("login")


class ValidatorView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return render(request, 'terminal.html')
        return redirect('login')

    def post(self, request):
        if request.user.is_authenticated:
            stake = float(request.POST['stake'])
            if blockchain.get_balance(request.user.username) >= stake:
                blockchain.add_validator(request.user.username, stake)
                # profile.is_validator = True
                # profile.save()
                return redirect('user_profile')
        return redirect('login')


class QRView(View):
    def get(self, request):
        if request.user.is_authenticated:
            user = User.objects.get(id=request.user.id)
            if not user.wallet_qr:
                qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
                qr.add_data(user.wallet_address)
                qr.make(fit=True)

                img = qr.make_image(fill='black', back_color='white')

                qr_image = BytesIO()
                img.save(qr_image, format='PNG')
                qr_image.seek(0)

                qr_file = ContentFile(qr_image.read(), name=f'{user.wallet_address}_qr.png')
                user.wallet_qr = qr_file
                user.save()
            return render(request, 'qr.html', {'user': user})
        return redirect('login')