from .encryption import custom_encrypt, custom_decrypt

class EncryptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Decrypt incoming data
        if request.method == 'POST':
            request.POST = {k: custom_decrypt(v) for k, v in request.POST.items()}

        response = self.get_response(request)

        # Encrypt outgoing data
        if response.get('Content-Type', '').startswith('text/html'):
            content = response.content.decode('utf-8')
            encrypted_content = custom_encrypt(content)
            response.content = encrypted_content.encode('utf-8')

        return response