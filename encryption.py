from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import hashlib
import base64

def generate_key(user_id):
    user_id_str = str(user_id)
    short_key = user_id_str[:2] + user_id_str[-2:]
    return hashlib.sha256(short_key.encode()).digest()[:16]

def encrypt_message(message, user_id):
    key = generate_key(user_id)
    iv = get_random_bytes(16)  # Initialization Vector
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(message.encode(), AES.block_size))
    return base64.b64encode(iv + encrypted).decode()

def decrypt_message(encrypted_b64, user_id):
    key = generate_key(user_id)
    data = base64.b64decode(encrypted_b64)
    iv = data[:16]
    encrypted = data[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = unpad(cipher.decrypt(encrypted), AES.block_size)
    return decrypted.decode()

