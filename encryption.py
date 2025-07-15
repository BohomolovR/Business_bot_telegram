from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import hashlib
import base64



class MessageEncryptor:
    def generate_key(self, owner_id):
        user_id_str = str(owner_id)
        short_key = user_id_str[:2] + user_id_str[-2:]
        return hashlib.sha256(short_key.encode()).digest()[:16]

    def encrypt_message(self, message, owner_id):
        key = self.generate_key(owner_id)
        iv = get_random_bytes(16)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        encrypted = cipher.encrypt(pad(message.encode(), AES.block_size))
        return base64.b64encode(iv + encrypted).decode()

    def decrypt_message(self, message, owner_id):
        key = self.generate_key(owner_id)
        data = base64.b64decode(message)
        iv = data[:16]
        encrypted = data[16:]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = unpad(cipher.decrypt(encrypted), AES.block_size)
        return decrypted.decode()





